#!/bin/bash
echo "y" | docker run -i --rm -v $(pwd):/workspace -w /workspace kivy/buildozer android debug
