#!/usr/bin/env python3
"""Volt Medusa — neon jellyfish pulse-glide arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/home/workdir/artifacts/VOLT_MEDUSA_ElbowOS.mp4")
TITLE, HANDLE = "VOLT MEDUSA", "x.com/ElbowOS"

ABYSS = (6, 8, 28)
INK = (12, 22, 52)
CYAN = (48, 255, 232)
MAG = (255, 64, 196)
LIME = (176, 255, 72)
VIO = (150, 96, 255)
GOLD = (255, 220, 110)
WHITE = (246, 252, 255)
HOT = (255, 62, 96)
TEAL = (28, 186, 210)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.font_lg = pygame.font.SysFont("DejaVu Sans", 54, bold=True)
        self.font = pygame.font.SysFont("DejaVu Sans", 34, bold=True)
        self.font_sm = pygame.font.SysFont("DejaVu Sans", 26)
        self.clock = pygame.time.Clock()
        self.score = self.t = self.flash = self.pulse_cd = 0
        self.pulse = 0
        self.sparks, self.rings, self.wakes = [], [], []
        self.dust = [[random.randint(0, W), random.uniform(0, 5000),
                      random.uniform(0.6, 2.2), random.choice((CYAN, MAG, VIO, LIME))]
                     for _ in range(90)]
        self.reset()

    def reset(self):
        self.lives = 3
        self.px, self.py = W / 2, 900.0
        self.vx, self.vy = 0.0, -7.2
        self.cam = self.py - H * 0.62
        self.motes, self.urchins, self.eels = [], [], []
        self.currents = []
        self.next_y = 200
        while self.next_y < self.py + 2600:
            self.spawn_band(self.next_y)
            self.next_y += 260
        self.phase = 0.0

    def burst(self, x, y, col, n=14):
        for _ in range(n):
            a = random.uniform(0, 6.2832)
            sp = random.uniform(2, 12)
            self.sparks.append([x, y, math.cos(a) * sp, math.sin(a) * sp, 18, col])

    def spawn_band(self, y):
        lane = (int(y) // 260) % 3
        cx = 220 + lane * 320 + random.uniform(-40, 40)
        self.currents.append({"x": cx, "y": y, "w": random.uniform(90, 140),
                              "dir": 1 if lane != 1 else -1, "amp": random.uniform(1.4, 2.6)})
        for _ in range(4):
            self.motes.append({"x": random.uniform(90, W - 90),
                               "y": y + random.uniform(-100, 100),
                               "alive": True, "ph": random.random() * 6})
        if random.random() < 0.7:
            self.urchins.append({"x": random.choice([160, W / 2, W - 160]) + random.uniform(-70, 70),
                                 "y": y + random.uniform(-50, 70), "r": random.randint(28, 40),
                                 "ang": random.random() * 6})
        if random.random() < 0.5:
            self.eels.append({"x": random.uniform(140, W - 140), "y": y,
                              "amp": random.uniform(70, 140), "ph": random.random() * 6,
                              "len": random.randint(5, 8)})

    def do_pulse(self):
        if self.pulse_cd > 0:
            return
        self.pulse_cd = 16
        self.pulse = 14
        self.vy -= 9.5
        self.burst(self.px, self.py, CYAN, 18)
        self.rings.append([self.px, self.py, 12, CYAN])
        for m in self.motes:
            if m["alive"] and math.hypot(m["x"] - self.px, m["y"] - self.py) < 130:
                m["alive"] = False
                self.score += 20
                self.burst(m["x"], m["y"], LIME, 8)
                self.rings.append([m["x"], m["y"], 6, LIME])

    def autoplay(self):
        best, bd = None, 1e9
        for m in self.motes:
            if not m["alive"]:
                continue
            dy = m["y"] - self.py
            if dy < -80:
                continue
            d = math.hypot(m["x"] - self.px, dy)
            if d < bd:
                best, bd = m, d
        threat = False
        for u in self.urchins:
            if abs(u["y"] - self.py) < 160 and abs(u["x"] - self.px) < u["r"] + 70:
                threat = True
                self.vx += -3.2 if self.px > u["x"] else 3.2
        if best and not threat:
            self.vx += (best["x"] - self.px) * 0.018
            if bd < 150 and self.pulse_cd == 0 and best["y"] < self.py + 40:
                self.do_pulse()
        elif self.t % 38 == 0 and self.pulse_cd == 0:
            self.do_pulse()
        self.vx += math.sin(self.t * 0.07) * 0.15

    def tick(self):
        self.t += 1
        self.flash = max(0, self.flash - 1)
        self.pulse_cd = max(0, self.pulse_cd - 1)
        self.pulse = max(0, self.pulse - 1)
        self.phase += 0.08
        drift = 0.0
        for c in self.currents:
            if abs(c["y"] - self.py) < 160 and abs(c["x"] - self.px) < c["w"]:
                drift += c["dir"] * c["amp"]
        self.vx += drift * 0.18
        self.vy += -0.08
        self.vy = max(-16.0, min(-3.5, self.vy))
        self.vx *= 0.92
        self.px += self.vx
        self.py += self.vy
        self.px = max(70, min(W - 70, self.px))
        if self.px in (70, W - 70):
            self.vx *= -0.55
        self.cam += ((self.py - H * 0.62) - self.cam) * 0.14
        while self.next_y < self.py + 2600:
            self.spawn_band(self.next_y)
            self.next_y += 260
        cut = self.cam - 240
        self.currents = [c for c in self.currents if c["y"] > cut]
        self.motes = [m for m in self.motes if m["y"] > cut]
        self.urchins = [u for u in self.urchins if u["y"] > cut]
        self.eels = [e for e in self.eels if e["y"] > cut]
        pr = 26 + (8 if self.pulse else 0)
        for m in self.motes:
            if m["alive"] and math.hypot(m["x"] - self.px, m["y"] - self.py) < pr + 10:
                m["alive"] = False
                self.score += 12
                self.burst(m["x"], m["y"], MAG, 9)
        for u in self.urchins:
            u["ang"] += 0.09
            if math.hypot(u["x"] - self.px, u["y"] - self.py) < u["r"] + 16:
                self.lives -= 1
                self.flash = 9
                self.burst(self.px, self.py, HOT, 24)
                self.px += -80 if self.px > u["x"] else 80
                self.vy = -11
                if self.lives <= 0:
                    self.score = max(0, self.score - 20)
                    self.reset()
        for e in self.eels:
            e["ph"] += 0.11
            hx = e["x"] + math.sin(e["ph"]) * e["amp"]
            if math.hypot(hx - self.px, e["y"] - self.py) < 22:
                self.lives -= 1
                self.flash = 8
                self.burst(self.px, self.py, VIO, 16)
                self.vy = -10
                if self.lives <= 0:
                    self.reset()
        if self.t % 5 == 0:
            self.score += 1
        if self.t % 3 == 0:
            self.wakes.append([self.px, self.py + 18, 10, CYAN])
        for w in self.wakes:
            w[2] += 3
        self.wakes = [w for w in self.wakes if w[2] < 70]
        for sp in self.sparks:
            sp[0] += sp[2]; sp[1] += sp[3]; sp[4] -= 1
        self.sparks = [sp for sp in self.sparks if sp[4] > 0]
        for r in self.rings:
            r[2] += 7
        self.rings = [r for r in self.rings if r[2] < 150]
        for d in self.dust:
            d[1] += d[2]
            if d[1] > self.cam + H + 40:
                d[1] = self.cam - 30
                d[0] = random.randint(0, W)

    def sy(self, y):
        return int(y - self.cam)

    def draw(self, surf):
        surf.fill(ABYSS)
        for i in range(14):
            y0 = (i * 160 + int(self.t * 4)) % (H + 80) - 40
            pygame.draw.rect(surf, INK, (0, y0, W, 8))
        for i in range(8):
            y = i * 280 - (int(self.cam * 0.4) % 280)
            pygame.draw.polygon(surf, (10, 36, 64), [(0, y), (90, y + 90), (0, y + 200)])
            pygame.draw.polygon(surf, (10, 36, 64), [(W, y), (W - 90, y + 90), (W, y + 200)])
        pygame.draw.rect(surf, CYAN, (16, 210, 7, 1500))
        pygame.draw.rect(surf, MAG, (W - 23, 210, 7, 1500))
        for d in self.dust:
            pygame.draw.circle(surf, d[3], (int(d[0]), self.sy(d[1])), 2)
        for c in self.currents:
            y = self.sy(c["y"])
            if -80 < y < H + 80:
                rec = pygame.Surface((int(c["w"] * 2), 180), pygame.SRCALPHA)
                rec.fill((48, 255, 232, 22))
                surf.blit(rec, (int(c["x"] - c["w"]), y - 90))
        for m in self.motes:
            if not m["alive"]:
                continue
            y = self.sy(m["y"])
            if -20 < y < H + 20:
                s = 7 + int(3 * math.sin(self.t * 0.2 + m["ph"]))
                pygame.draw.circle(surf, LIME, (int(m["x"]), y), s)
                pygame.draw.circle(surf, WHITE, (int(m["x"]) - 2, y - 2), 3)
        for u in self.urchins:
            y = self.sy(u["y"])
            if -50 < y < H + 50:
                pts = []
                for i in range(12):
                    a = u["ang"] + i * (math.pi / 6)
                    rr = u["r"] if i % 2 == 0 else u["r"] * 0.55
                    pts.append((u["x"] + math.cos(a) * rr, y + math.sin(a) * rr))
                pygame.draw.polygon(surf, HOT, pts)
                pygame.draw.circle(surf, (40, 8, 28), (int(u["x"]), y), 11)
        for e in self.eels:
            pts = []
            for i in range(e["len"]):
                yy = e["y"] + i * 18
                xx = e["x"] + math.sin(e["ph"] + i * 0.55) * e["amp"]
                pts.append((xx, self.sy(yy)))
            if pts:
                pygame.draw.lines(surf, VIO, False, pts, 8)
                pygame.draw.circle(surf, MAG, (int(pts[0][0]), int(pts[0][1])), 10)
        for w in self.wakes:
            pygame.draw.circle(surf, w[3], (int(w[0]), self.sy(w[1])), int(w[2]), 2)
        for r in self.rings:
            pygame.draw.circle(surf, r[3], (int(r[0]), self.sy(r[1])), int(r[2]), 2)
        for sp in self.sparks:
            pygame.draw.circle(surf, sp[5], (int(sp[0]), self.sy(sp[1])), max(2, sp[4] // 4))
        px, py = int(self.px), self.sy(self.py)
        for k in range(5):
            a = math.pi * 0.55 + k * 0.25 + math.sin(self.t * 0.18 + k) * 0.25
            tx = px + math.cos(a) * (38 + 8 * math.sin(self.t * 0.25 + k))
            ty = py + 22 + math.sin(a) * 10 + k * 10
            pygame.draw.line(surf, MAG, (px, py + 8), (tx, ty), 4)
            pygame.draw.circle(surf, CYAN, (int(tx), int(ty)), 4)
        rad = 28 + (10 if self.pulse else int(4 * math.sin(self.t * 0.2)))
        pygame.draw.circle(surf, (20, 70, 90), (px, py), rad + 8)
        pygame.draw.ellipse(surf, CYAN, (px - rad, py - rad + 6, rad * 2, int(rad * 1.5)))
        pygame.draw.ellipse(surf, MAG, (px - rad + 8, py - rad + 14, rad * 2 - 16, int(rad * 0.9)))
        pygame.draw.circle(surf, WHITE, (px - 8, py - 4), 7)
        pygame.draw.circle(surf, ABYSS, (px - 6, py - 3), 3)
        if self.flash:
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((255, 62, 96, 70))
            surf.blit(ov, (0, 0))
        title = self.font_lg.render(TITLE, True, CYAN)
        surf.blit(title, title.get_rect(center=(W // 2, 84)))
        sub = self.font_sm.render(HANDLE, True, MAG)
        surf.blit(sub, sub.get_rect(center=(W // 2, 146)))
        sc = self.font.render(f"SCORE  {self.score}", True, WHITE)
        lv = self.font.render(f"LIVES  {'\u25c6' * max(0, self.lives)}", True, LIME)
        md = self.font_sm.render("PULSE" if self.pulse else "GLIDE", True, GOLD)
        surf.blit(sc, sc.get_rect(center=(W // 2, H - 168)))
        surf.blit(lv, lv.get_rect(center=(W // 2, H - 108)))
        surf.blit(md, md.get_rect(center=(W // 2, H - 58)))

    def play_interactive(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.score = 0
                    self.reset()
                elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.do_pulse()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vx -= 0.85
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vx += 0.85
            self.tick()
            self.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    def record(self):
        frames = FPS * SECS
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart",
            OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        canvas = pygame.Surface((W, H))
        try:
            for i in range(frames):
                self.autoplay()
                self.tick()
                self.draw(canvas)
                proc.stdin.write(pygame.image.tostring(canvas, "RGB"))
                if i % 30 == 0:
                    print(f"frame {i}/{frames}", flush=True)
        finally:
            proc.stdin.close()
            err = proc.stderr.read().decode("utf-8", "ignore")
            rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
