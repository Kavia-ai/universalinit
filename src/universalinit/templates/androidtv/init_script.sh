#!/bin/bash

PROJECT_NAME=$1
OUTPUT_DIR=${2:-.}

echo "🚀 Initializing Android TV project: $PROJECT_NAME"

# Step 1: Use Gradle to create base Android app
echo "📦 Creating base Android project..."
gradle init \
  -Dorg.gradle.buildinit.specs=org.gradle.experimental.android-ecosystem-init:0.1.44 \
  -Dorg.gradle.buildinit.language=kotlin \
  --use-defaults \
  --overwrite

if [ $? -ne 0 ]; then
    echo "❌ Failed to create Android project"
    exit 1
fi

echo "📺 Converting to Android TV..."

# Step 2: Modify build.gradle.kts to add TV dependencies
cat >> app/build.gradle.kts << 'EOF'

dependencies {
    // Android TV Libraries
    implementation("androidx.leanback:leanback:1.0.0")
    implementation("androidx.tvprovider:tvprovider:1.0.0")
    
    // ExoPlayer for video
    implementation("androidx.media3:media3-exoplayer:1.2.1")
    implementation("androidx.media3:media3-ui:1.2.1")
    
    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    
    // Image loading
    implementation("com.github.bumptech.glide:glide:4.16.0")
}
EOF

# Step 3: Update AndroidManifest.xml for TV
MANIFEST_PATH="app/src/main/AndroidManifest.xml"

if [ -f "$MANIFEST_PATH" ]; then
    # Add TV features after <manifest> tag
    sed -i '/<manifest/a\
    \
    <!-- Required for Android TV -->\
    <uses-feature\
        android:name="android.software.leanback"\
        android:required="true" />\
    \
    <uses-feature\
        android:name="android.hardware.touchscreen"\
        android:required="false" />\
    \
    <uses-permission android:name="android.permission.INTERNET" />' "$MANIFEST_PATH"
    
    # Change launcher category to LEANBACK_LAUNCHER
    sed -i 's/android.intent.category.LAUNCHER/android.intent.category.LEANBACK_LAUNCHER/g' "$MANIFEST_PATH"
    
    # Add TV theme
    sed -i 's/android:theme="@style\/[^"]*"/android:theme="@style\/Theme.Leanback"/g' "$MANIFEST_PATH"
fi

# Step 4: Create TV-specific directories
mkdir -p app/src/main/res/drawable
mkdir -p app/src/main/java/com/example/$PROJECT_NAME/ui/rating
mkdir -p app/src/main/java/com/example/$PROJECT_NAME/ui/player

# Step 5: Lower minSdk for TV compatibility
sed -i 's/minSdk = [0-9]*/minSdk = 21/g' app/build.gradle.kts

echo ""
echo "✅ Android TV project created successfully!"
echo ""
echo "📁 Project structure:"
echo "  ├── app/"
echo "  │   ├── build.gradle.kts (TV dependencies added)"
echo "  │   └── src/main/"
echo "  │       ├── AndroidManifest.xml (TV features enabled)"
echo "  │       └── java/com/example/$PROJECT_NAME/"
echo ""
echo "🎯 Next steps:"
echo "  1. ./gradlew assembleDebug"
echo "  2. Connect Android TV: adb connect <TV_IP>:5555"
echo "  3. ./gradlew installDebug"
echo ""
