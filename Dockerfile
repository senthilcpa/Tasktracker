FROM kivy/buildozer:latest

# Pre-accept Android SDK licenses
RUN mkdir -p /root/.android && \
    echo "y" | /opt/android-sdk/tools/bin/sdkmanager --licenses && \
    echo "y" | /opt/android-sdk/tools/bin/sdkmanager --update

# Set environment variable to allow root
ENV BUILDOZER_ALLOW_ROOT=1