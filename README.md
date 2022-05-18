Linux/python utility to join gopro video file parts together, maintaining the gyro data. For use with gyroflow etc.

### Using

Link join.py in ~/.local/bin or otherwise add it to your PATH

And then, in any directory that contains gopro files, run

```
join-gopro.py
```

All the appropriate gopro video parts in the current directory will be joined together.

### Credits

This uses ffmpeg and the GoPro labs tool udtacopy

https://gopro.github.io/labs/control/chapters/
