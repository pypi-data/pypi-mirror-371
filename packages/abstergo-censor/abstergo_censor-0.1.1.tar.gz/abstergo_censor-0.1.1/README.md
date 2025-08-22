# PlainSight

Privacy-first CLI that blurs faces and license plates in images and videos using OpenCV's cascades.

```bash
pip install -r requirements.txt
python plainsight.py input.jpg --out out.jpg
python plainsight.py input.mp4 --out out.mp4
```

Options:
- `--plates` to enable license plate detection
- `--strength 25` blur kernel size (odd integer)
- `--show` to preview window
- `--scale 1.2` detection scale factor

## Notes
- Uses OpenCV Haar cascades available in `cv2.data.haarcascades`
- Works offline, no cloud calls
- Good default for quick anonymization; not perfect for edge cases

## License
MIT
