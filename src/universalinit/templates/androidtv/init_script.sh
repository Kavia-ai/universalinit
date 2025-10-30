#!/bin/bash
set -e  # Exit on any error

PROJECT_NAME_RAW=${1:-"AndroidTVApp"}
MIN_SDK=${2:-21}
TARGET_SDK=${3:-34}

# ============================================================================
# Sanitize project name for Android package naming
# Android package names:
# - Cannot contain hyphens, spaces, or special characters
# - Can only use letters, numbers, and underscores
# - Each segment must start with a letter
# ============================================================================
# Convert to valid package name: replace hyphens/spaces with underscores, remove special chars
PROJECT_NAME=$(echo "$PROJECT_NAME_RAW" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g' | sed 's/^_*//' | sed 's/_*$//')

# Ensure it starts with a letter (if it starts with number, prepend 'app')
if [[ $PROJECT_NAME =~ ^[0-9] ]]; then
    PROJECT_NAME="app_${PROJECT_NAME}"
fi

# Use raw name for display, sanitized name for package
DISPLAY_NAME="$PROJECT_NAME_RAW"

echo "🚀 Initializing Android TV project: $DISPLAY_NAME"
echo "📦 Package name: com.example.$PROJECT_NAME"
echo "📋 Configuration: minSdk=$MIN_SDK, targetSdk=$TARGET_SDK"

# ============================================================================
# Step 1: Detect Android SDK
# ============================================================================
echo "🔍 Detecting Android SDK..."

ANDROID_SDK=""
if [ -n "$ANDROID_HOME" ]; then
    ANDROID_SDK="$ANDROID_HOME"
elif [ -n "$ANDROID_SDK_ROOT" ]; then
    ANDROID_SDK="$ANDROID_SDK_ROOT"
elif [ -d "$HOME/Library/Android/sdk" ]; then
    ANDROID_SDK="$HOME/Library/Android/sdk"
elif [ -d "/usr/local/android-sdk" ]; then
    ANDROID_SDK="/usr/local/android-sdk"
else
    echo "⚠️  Warning: Android SDK not found. Build may fail."
    echo "   Set ANDROID_HOME or install Android Studio"
fi

if [ -n "$ANDROID_SDK" ]; then
    echo "✅ Android SDK found: $ANDROID_SDK"
    cat > local.properties << EOF
sdk.dir=$ANDROID_SDK
EOF
else
    echo "⚠️  No local.properties created - SDK not detected"
fi

# ============================================================================
# Step 2: Bootstrap Gradle Wrapper
# ============================================================================
echo ""
echo "📦 Setting up Gradle Wrapper..."

mkdir -p gradle/wrapper

# Create gradle-wrapper.properties
cat > gradle/wrapper/gradle-wrapper.properties << 'EOF'
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.7-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

# Download gradle-wrapper.jar from official Gradle services
echo "⬇️  Downloading Gradle Wrapper JAR..."
curl -sSL -o gradle/wrapper/gradle-wrapper.jar \
     https://raw.githubusercontent.com/gradle/gradle/v8.7.0/gradle/wrapper/gradle-wrapper.jar

# Download gradlew scripts
echo "⬇️  Downloading Gradle Wrapper scripts..."
curl -sSL -o gradlew \
     https://raw.githubusercontent.com/gradle/gradle/v8.7.0/gradlew
curl -sSL -o gradlew.bat \
     https://raw.githubusercontent.com/gradle/gradle/v8.7.0/gradlew.bat

chmod +x gradlew

echo "✅ Gradle Wrapper ready"

# ============================================================================
# Step 3: Create Project Structure
# ============================================================================
echo ""
echo "📁 Creating project structure..."

mkdir -p app/src/main/java/com/example/${PROJECT_NAME}/
mkdir -p app/src/main/res/layout
mkdir -p app/src/main/res/values
mkdir -p app/src/main/res/drawable
mkdir -p app/src/main/res/drawable-xhdpi
mkdir -p app/src/test/java/com/example/${PROJECT_NAME}/

# ============================================================================
# Step 4: Create Root build.gradle.kts
# ============================================================================
echo "📝 Creating build configuration..."

cat > build.gradle.kts << 'EOF'
// Top-level build file
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:8.3.0")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.22")
    }
}

plugins {
    id("com.android.application") version "8.3.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.layout.buildDirectory)
}
EOF

# ============================================================================
# Step 5: Create settings.gradle.kts
# ============================================================================
cat > settings.gradle.kts << EOF
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "$DISPLAY_NAME"
include(":app")
EOF

# ============================================================================
# Step 6: Create gradle.properties
# ============================================================================
cat > gradle.properties << 'EOF'
# Project-wide Gradle settings
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
org.gradle.parallel=true
org.gradle.caching=true

# Android
android.useAndroidX=true
android.enableJetifier=true

# Kotlin
kotlin.code.style=official
EOF

# ============================================================================
# Step 7: Create app/build.gradle.kts
# ============================================================================
cat > app/build.gradle.kts << EOF
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.${PROJECT_NAME}"
    compileSdk = $TARGET_SDK

    defaultConfig {
        applicationId = "com.example.${PROJECT_NAME}"
        minSdk = $MIN_SDK
        targetSdk = $TARGET_SDK
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    // Android TV Core
    implementation("androidx.leanback:leanback:1.0.0")
    implementation("androidx.tvprovider:tvprovider:1.0.0")
    
    // AndroidX Core
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // Lifecycle
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.fragment:fragment-ktx:1.6.2")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    
    // ExoPlayer for video
    implementation("androidx.media3:media3-exoplayer:1.2.1")
    implementation("androidx.media3:media3-ui:1.2.1")
    implementation("androidx.media3:media3-exoplayer-dash:1.2.1")
    implementation("androidx.media3:media3-exoplayer-hls:1.2.1")
    
    // Image loading
    implementation("com.github.bumptech.glide:glide:4.16.0")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}
EOF

# ============================================================================
# Step 8: Create app/proguard-rules.pro
# ============================================================================
cat > app/proguard-rules.pro << 'EOF'
# Add project specific ProGuard rules here.
-keepattributes *Annotation*
-keepattributes Signature, InnerClasses, EnclosingMethod

# Retrofit
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# Gson
-keepclassmembers,allowobfuscation class * {
  @com.google.gson.annotations.SerializedName <fields>;
}

# ExoPlayer
-keep class androidx.media3.** { *; }
-dontwarn androidx.media3.**
EOF

# ============================================================================
# Step 9: Create AndroidManifest.xml (TV-optimized)
# ============================================================================
cat > app/src/main/AndroidManifest.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Required for Android TV -->
    <uses-feature
        android:name="android.software.leanback"
        android:required="true" />

    <!-- Touchscreen not required for TV -->
    <uses-feature
        android:name="android.hardware.touchscreen"
        android:required="false" />

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher"
        android:label="$DISPLAY_NAME"
        android:theme="@style/AppTheme"
        android:banner="@drawable/app_banner">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="landscape">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LEANBACK_LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
EOF

# ============================================================================
# Step 10: Create MainActivity.kt
# ============================================================================
cat > app/src/main/java/com/example/${PROJECT_NAME}/MainActivity.kt << EOF
package com.example.${PROJECT_NAME}

import android.os.Bundle
import androidx.fragment.app.FragmentActivity
import android.view.KeyEvent
import android.widget.TextView

/**
 * Main Activity for Android TV
 * Extends FragmentActivity for Leanback compatibility
 */
class MainActivity : FragmentActivity() {

    private lateinit var titleText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        titleText = findViewById(R.id.title_text)
        titleText.text = "$DISPLAY_NAME"
        
        // TODO: Initialize your rating screen components here
        // setupRatingOverlay()
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        // Handle TV remote control inputs
        return when (keyCode) {
            KeyEvent.KEYCODE_DPAD_CENTER,
            KeyEvent.KEYCODE_ENTER -> {
                // Handle SELECT/OK button
                true
            }
            KeyEvent.KEYCODE_BACK -> {
                // Handle BACK button
                finish()
                true
            }
            else -> super.onKeyDown(keyCode, event)
        }
    }
}
EOF

# ============================================================================
# Step 11: Create activity_main.xml layout
# ============================================================================
cat > app/src/main/res/layout/activity_main.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#000000">

    <TextView
        android:id="@+id/title_text"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="$DISPLAY_NAME"
        android:textSize="48sp"
        android:textColor="#FFFFFF"
        android:focusable="true"
        android:focusableInTouchMode="true"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/subtitle_text"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Ready for rating screen integration"
        android:textSize="24sp"
        android:textColor="#CCCCCC"
        android:layout_marginTop="24dp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@id/title_text" />

</androidx.constraintlayout.widget.ConstraintLayout>
EOF

# ============================================================================
# Step 12: Create strings.xml
# ============================================================================
cat > app/src/main/res/values/strings.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">$DISPLAY_NAME</string>
    
    <!-- Rating Screen Strings -->
    <string name="rating_title">Did you like it?</string>
    <string name="rating_message">Your vote helps us recommend more content like this.</string>
    <string name="rating_like">I like it</string>
    <string name="rating_love">I love it</string>
    <string name="rating_dislike">I don\'t like it</string>
    <string name="rating_close">Close</string>
    <string name="rating_countdown">Closing in %d seconds</string>
</resources>
EOF

# ============================================================================
# Step 13: Create colors.xml
# ============================================================================
cat > app/src/main/res/values/colors.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- TV optimized colors -->
    <color name="tv_background">#000000</color>
    <color name="tv_overlay">#CC000000</color>
    <color name="tv_primary">#FFFFFF</color>
    <color name="tv_secondary">#CCCCCC</color>
    <color name="tv_accent">#2196F3</color>
    <color name="tv_button_focused">#FFFFFF</color>
    <color name="tv_button_normal">#80FFFFFF</color>
</resources>
EOF

# ============================================================================
# Step 14: Create styles.xml
# ============================================================================
cat > app/src/main/res/values/styles.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Base application theme for Android TV -->
    <style name="AppTheme" parent="Theme.Leanback">
        <!-- Customize your theme here -->
        <item name="android:windowBackground">@color/tv_background</item>
        <item name="android:colorPrimary">@color/tv_accent</item>
    </style>
</resources>
EOF

# ============================================================================
# Step 15: Create Launcher Icon
# ============================================================================
cat > app/src/main/res/drawable/ic_launcher.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    
    <!-- Background -->
    <path
        android:fillColor="#2196F3"
        android:pathData="M0,0h108v108h-108z"/>
    
    <!-- Icon shape (play button for TV) -->
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M 40,30 L 40,78 L 80,54 Z"/>
</vector>
EOF

# ============================================================================
# Step 16: Create TV Banner
# ============================================================================
cat > app/src/main/res/drawable/app_banner.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="320dp"
    android:height="180dp"
    android:viewportWidth="320"
    android:viewportHeight="180">
    
    <!-- Banner background -->
    <path
        android:fillColor="#1976D2"
        android:pathData="M0,0h320v180h-320z"/>
    
    <!-- App name text background -->
    <path
        android:fillColor="#0D47A1"
        android:pathData="M20,60h280v60h-280z"/>
    
    <!-- Decorative play icon -->
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M 50,75 L 50,105 L 80,90 Z"/>
    
    <!-- Banner for $DISPLAY_NAME -->
</vector>
EOF

# ============================================================================
# Step 17: Create High-Res Drawable Icon
# ============================================================================
cat > app/src/main/res/drawable-xhdpi/ic_launcher_fallback.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="96dp"
    android:height="96dp"
    android:viewportWidth="96"
    android:viewportHeight="96">
    
    <path
        android:fillColor="#2196F3"
        android:pathData="M0,0h96v96h-96z"/>
    
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M 35,25 L 35,71 L 72,48 Z"/>
</vector>
EOF

# ============================================================================
# Step 18: Create basic Unit Test
# ============================================================================
cat > app/src/test/java/com/example/${PROJECT_NAME}/ExampleUnitTest.kt << EOF
package com.example.${PROJECT_NAME}

import org.junit.Test
import org.junit.Assert.*

/**
 * Example local unit test, which will execute on the development machine (host).
 */
class ExampleUnitTest {
    @Test
    fun addition_isCorrect() {
        assertEquals(4, 2 + 2)
    }
}
EOF

# ============================================================================
# Step 19: Create .gitignore
# ============================================================================
cat > .gitignore << 'EOF'
# Built application files
*.apk
*.aab
*.ap_
*.dex

# Files for the Dalvik VM
*.class

# Generated files
bin/
gen/
out/
build/
.gradle/

# Gradle files
.gradle
gradle-app.setting
!gradle-wrapper.jar
.gradletasknamecache

# Local configuration
local.properties

# IntelliJ
*.iml
.idea/
*.ipr
*.iws

# Android Studio
.navigation/
captures/
.externalNativeBuild
.cxx/

# Keystore files
*.jks
*.keystore

# Lint
lint/
*.log
EOF

# ============================================================================
# Done!
# ============================================================================
echo ""
echo "✅ Android TV project created successfully!"
echo ""
echo "📁 Project structure:"
echo "  ├── app/"
echo "  │   ├── build.gradle.kts (TV dependencies)"
echo "  │   └── src/"
echo "  │       ├── main/"
echo "  │       │   ├── AndroidManifest.xml (TV-optimized)"
echo "  │       │   ├── java/com/example/$PROJECT_NAME/"
echo "  │       │   │   └── MainActivity.kt"
echo "  │       │   └── res/"
echo "  │       │       ├── layout/activity_main.xml"
echo "  │       │       ├── values/"
echo "  │       │       │   ├── strings.xml"
echo "  │       │       │   ├── colors.xml"
echo "  │       │       │   └── styles.xml"
echo "  │       │       └── drawable/"
echo "  │       │           ├── ic_launcher.xml (launcher icon)"
echo "  │       │           └── app_banner.xml (TV banner)"
echo "  │       └── test/"
echo "  ├── build.gradle.kts"
echo "  ├── settings.gradle.kts"
echo "  ├── gradlew"
echo "  └── local.properties (SDK: $ANDROID_SDK)"
echo ""
echo "📦 Package name: com.example.$PROJECT_NAME"
echo "📺 Display name: $DISPLAY_NAME"
echo ""
echo "🎯 Next steps:"
echo "  1. Build project:    ./gradlew assembleDebug"
echo "  2. Run tests:        ./gradlew test"
echo "  3. Install to TV:    ./gradlew installDebug"
echo ""
echo "📺 Connect Android TV device:"
echo "  adb connect <TV_IP>:5555"
echo ""
echo "💡 Note: Project name sanitized for Android package naming"
echo "   Original: $PROJECT_NAME_RAW"
echo "   Package:  $PROJECT_NAME"
echo ""
echo "🎬 Ready to add your rating screen implementation!"
echo ""
