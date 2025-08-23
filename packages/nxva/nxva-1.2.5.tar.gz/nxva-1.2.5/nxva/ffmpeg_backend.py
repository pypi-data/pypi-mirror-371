import os
import sys
import time
import shlex
import select
import logging
import threading
import subprocess as sp
import numpy as np

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

BAD_SIGS = (
    b"Impossible to convert between the formats",
    b"Failed to inject frame into filter network",
    b"Function not implemented",
    b"No device available for decoder",
)

def drain_stderr(proc):
    """把 ffmpeg 的 stderr 持續讀掉，避免阻塞；同時把訊息印出方便除錯。"""
    for line in iter(proc.stderr.readline, b''):
        try:
            sys.stderr.write("[ffmpeg] " + line.decode("utf-8", "ignore"))
        except Exception:
            pass


def build_cmd(rtsp_url, w, h, fps=5, hwaccel=True):
    if hwaccel:
        return [
            "ffmpeg",
            "-v", "warning",          # 日誌等級（warning/info），不影響資料流
            "-nostats",               # 不印進度統計，省 I/O

            # ===== 輸入端（RTSP）選項 =====
            "-rtsp_transport", "tcp",
            "-rtsp_flags", "prefer_tcp",

            # ===== 解碼與硬體幀格式 =====
            "-hwaccel", "drm",
            "-hwaccel_output_format", "drm_prime",
            # → 告訴 ffmpeg：若可，使用 DRM 路徑硬解（RPi 會走 V4L2-request）
            #   解碼出的每一幀是「GPU/驅動的 DMABUF」（drm_prime），不在 CPU 記憶體

            # 若需要明確指定 DRM render 節點，解除註解下面兩行：
            # "-init_hw_device", "drm=drm:/dev/dri/renderD128",
            # "-filter_hw_device", "drm",

            "-i", rtsp_url,

            # ===== 關掉不需要的流（節省工作）=====
            "-an", "-sn", "-dn",      # 不處理音訊/字幕/資料流

            # ===== swscale 全域旗標（套用到 scale 濾鏡）=====
            "-sws_flags", "fast_bilinear",  
            # → 指定 CPU 快速縮放演算法（犧牲些許質量，換取速度）

            # ===== 濾鏡鏈（filter graph）===== 
            "-vf", f"fps={fps},hwdownload,format=nv12,scale={w}:{h},format=bgr24",
            #  1) fps=5
            #     調整輸出幀率，降低 CPU 從 DRM 取幀的負擔
            #  2) hwdownload
            #     把「drm_prime」硬體幀從 DMABUF 回拷(&轉換)成 CPU 幀
            #  3) format=nv12
            #     指定回拷後的 CPU 像素格式用 NV12（Y + 交錯 UV），這對接下來的縮放最快
            #  4) scale=OUT_W:OUT_H
            #     用 swscale 在 CPU 縮放（會吃到上面的 fast_bilinear）
            #  5) format=bgr24
            #     最後把色彩空間轉成 BGR 8:8:8，OpenCV 最相容

            "-pix_fmt", "bgr24",
            # → 指定「輸出視訊流」的像素格式。因為你下方要以 rawvideo 輸出，這會決定輸出每幀的資料排列

            "-fps_mode", "passthrough",
            # → 不做補幀/丟幀處理，照輸入節奏走（等價舊寫法 -vsync 0）

            # ===== 輸出端（給 Python）=====
            "-f", "rawvideo", "pipe:1",
            # → 用 rawvideo muxer 把畫面逐幀吐到 stdout
        ]
    else:
        return [
            "ffmpeg",
            "-v", "error", "-nostats",
            "-rtsp_transport", "tcp", "-rtsp_flags", "prefer_tcp",
            "-i", rtsp_url,
            "-an", "-sn", "-dn",
            "-sws_flags", "fast_bilinear", 
            "-vf", f"fps={fps},scale={w}:{h},format=bgr24", 
            "-pix_fmt", "bgr24",
            "-fps_mode", "passthrough",
            "-f", "rawvideo", "pipe:1",
        ]
    

class FFmpegCapture:
    """
    一個模擬 cv2.VideoCapture 介面的 Adapter：
      - open(rtsp) / isOpened() / read() / release() / get(prop)
      - 內建硬解→軟解 fallback
      - 以 raw BGR 幀從 stdout 讀入
    """
    is_ffmpeg = True

    def __init__(self, width, height, fps=5, hwaccel=True,
                 first_frame_timeout=5.0, frame_timeout=3.0):
        self.w, self.h = int(width), int(height)
        self.fps = int(fps)
        self.hwaccel = bool(hwaccel)
        self.first_frame_timeout = float(first_frame_timeout)
        self.frame_timeout = float(frame_timeout)

        self._url = None
        self._proc = None
        self._opened = False
        self._frame_size = self.w * self.h * 3  # bgr24
        self._buf = bytearray(self._frame_size)
        self._mv = memoryview(self._buf)

    def _start_proc(self, cmd):
        print("[cmd]", " ".join(shlex.quote(x) for x in cmd))
        p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=10**8)  # 10**8
        threading.Thread(target=drain_stderr, args=(p,), daemon=True).start()
        return p
    
    def _try_read_exact(self, proc, timeout_sec=1.5):
        """等待 stdout 可讀並嘗試讀滿一幀；失敗回傳 False。"""
        got = 0
        fd  = proc.stdout.fileno()
        deadline = time.time() + timeout_sec
        while got < self._frame_size:
            if time.time() > deadline:
                return False
            # 等待有資料可讀，避免阻塞
            r, _, _ = select.select([fd], [], [], 0.05)
            # print("[main] select", r)
            if not r:
                if proc.poll() is not None:  # 子行程已退出
                    print("[main] ffmpeg exited with code", proc.returncode)
                    return False
                continue
            n = proc.stdout.readinto(self._mv[got:])
            # if n is None:
            #     continue
            if not n:
                if proc.poll() is not None:
                    return False
                continue
            got += n
        return True
    
    def open(self, rtsp_url):
        self.release()
        self._url = rtsp_url

        # 先嘗試硬解
        cmd = build_cmd(rtsp_url, self.w, self.h, self.fps, hwaccel=self.hwaccel)
        self._proc = self._start_proc(cmd)
        if not self._try_read_exact(self._proc, self.first_frame_timeout):
            # 讀不到第一幀，或行程已退出 → fallback 到軟解
            try: self._proc.kill()
            except: pass
            cmd = build_cmd(rtsp_url, self.w, self.h, self.fps, hwaccel=False)
            self._proc = self._start_proc(cmd)
            if not self._try_read_exact(self._proc, self.first_frame_timeout):
                try: self._proc.kill()
                except: pass
                self._proc = None
                self._opened = False
                return False

        self._opened = True
        return True

    def isOpened(self):
        return bool(self._proc and self._proc.poll() is None and self._opened)
    
    def read(self):
        """
        回傳 (True, frame) 或 (False, None)。失敗時不丟例外，好讓上層做重連。
        """
        p = self._proc
        if not self.isOpened():
            return False, None
        ok = self._try_read_exact(p, self.frame_timeout)
        if not ok:
            return False, None
        frame = np.frombuffer(self._buf, dtype=np.uint8).reshape((self.h, self.w, 3))
        return True, frame.copy()
    
    def release(self):
        if self._proc:
            try: self._proc.terminate()
            except: pass
            self._proc = None
        self._opened = False

    def get(self, prop):
        # 模擬OpenCV 的 VideoCapture.get()，只支援少數屬性
        import cv2
        if prop == cv2.CAP_PROP_FRAME_WIDTH:  return float(self.w)
        if prop == cv2.CAP_PROP_FRAME_HEIGHT: return float(self.h)
        if prop == cv2.CAP_PROP_FPS:          return float(self.fps)
        if prop == cv2.CAP_PROP_FOURCC:       return 0.0
        return 0.0