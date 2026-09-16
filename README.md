# Volt Medusa

Full-colour Python 3 neon jellyfish pulse-glide arcade for [ElbowOS](https://x.com/ElbowOS).

Steer a glowing medusa up a vertical abyss trench. Ride cyan current columns, pulse to shock nearby lumens, and dodge spinning urchins plus violet eels.

## Play

```bash
pip install -r requirements.txt
python3 volt_medusa.py --play
```

- **A / D** or arrows — drift left / right
- **Space / W / Up** — pulse (burst upward + collect nearby motes)
- **R** — reset
- **Esc** — quit

## Record a 9:16 reel

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 volt_medusa.py --record
```

Writes a 15s 1080×1920 H.264 MP4 (CRF 20, +faststart).

## Links

- Featured account: https://x.com/ElbowOS
- Gameplay reel (Drive): https://drive.google.com/file/d/1DC5su9HQ5VBkNrX1RydhCTHWjQHP8Jfc/view
