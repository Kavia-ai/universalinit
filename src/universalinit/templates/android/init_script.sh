#!/bin/bash
set -e  # Exit on any error

# Parse arguments
PROJECT_NAME_RAW=${1:-"AndroidApp"}
# Parse --min-sdk and --target-sdk from arguments
MIN_SDK=24
TARGET_SDK=35

# Skip first argument (project name) and parse flags
shift
while [[ $# -gt 0 ]]; do
    case $1 in
        --min-sdk=*)
            MIN_SDK="${1#*=}"
            shift
            ;;
        --min-sdk)
            MIN_SDK="$2"
            shift 2
            ;;
        --target-sdk=*)
            TARGET_SDK="${1#*=}"
            shift
            ;;
        --target-sdk)
            TARGET_SDK="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

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

echo "🚀 Initializing Android project: $DISPLAY_NAME"
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
mkdir -p app/src/main/res/mipmap-hdpi
mkdir -p app/src/main/res/mipmap-mdpi
mkdir -p app/src/main/res/mipmap-xhdpi
mkdir -p app/src/main/res/mipmap-xxhdpi
mkdir -p app/src/main/res/mipmap-xxxhdpi
mkdir -p app/src/test/java/com/example/${PROJECT_NAME}/
mkdir -p app/src/androidTest/java/com/example/${PROJECT_NAME}/

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
    // AndroidX Core
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // Material Design
    implementation("com.google.android.material:material:1.11.0")
    
    // Lifecycle
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.fragment:fragment-ktx:1.6.2")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
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
EOF

# ============================================================================
# Step 9: Create AndroidManifest.xml
# ============================================================================
cat > app/src/main/AndroidManifest.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
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
import androidx.appcompat.app.AppCompatActivity
import com.example.${PROJECT_NAME}.databinding.ActivityMainBinding

/**
 * Main Activity for Android Application
 */
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        binding.textView.text = "Welcome to $DISPLAY_NAME"
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
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello World!"
        android:textSize="24sp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
EOF

# ============================================================================
# Step 12: Create strings.xml
# ============================================================================
cat > app/src/main/res/values/strings.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">$DISPLAY_NAME</string>
</resources>
EOF

# ============================================================================
# Step 13: Create colors.xml
# ============================================================================
cat > app/src/main/res/values/colors.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>
EOF

# ============================================================================
# Step 14: Create styles.xml
# ============================================================================
cat > app/src/main/res/values/styles.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Base application theme -->
    <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
        <!-- Customize your theme here -->
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryDark">@color/purple_700</item>
        <item name="colorAccent">@color/teal_200</item>
    </style>
</resources>
EOF

# ============================================================================
# Step 15: Create Launcher Icon (for all densities)
# ============================================================================
ICON_CONTENT='<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp"
    android:height="48dp"
    android:viewportWidth="48"
    android:viewportHeight="48">
    
    <path
        android:fillColor="#6200EE"
        android:pathData="M0,0h48v48h-48z"/>
    
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M24,12 L24,36 M12,24 L36,24"/>
</vector>'

# Create icon for all mipmap densities
echo "$ICON_CONTENT" > app/src/main/res/mipmap-mdpi/ic_launcher.xml
echo "$ICON_CONTENT" > app/src/main/res/mipmap-hdpi/ic_launcher.xml
echo "$ICON_CONTENT" > app/src/main/res/mipmap-xhdpi/ic_launcher.xml
echo "$ICON_CONTENT" > app/src/main/res/mipmap-xxhdpi/ic_launcher.xml
echo "$ICON_CONTENT" > app/src/main/res/mipmap-xxxhdpi/ic_launcher.xml

# ============================================================================
# Step 16: Create basic Unit Test
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
# Step 17: Create .gitignore
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
echo "✅ Android project created successfully!"
echo ""
echo "📁 Project structure:"
echo "  ├── app/"
echo "  │   ├── build.gradle.kts"
echo "  │   └── src/"
echo "  │       ├── main/"
echo "  │       │   ├── AndroidManifest.xml"
echo "  │       │   ├── java/com/example/$PROJECT_NAME/"
echo "  │       │   │   └── MainActivity.kt"
echo "  │       │   └── res/"
echo "  │       │       ├── layout/activity_main.xml"
echo "  │       │       └── values/"
echo "  │       │           ├── strings.xml"
echo "  │       │           ├── colors.xml"
echo "  │       │           └── styles.xml"
echo "  │       └── test/"
echo "  ├── build.gradle.kts"
echo "  ├── settings.gradle.kts"
echo "  ├── gradlew"
echo "  └── local.properties (SDK: $ANDROID_SDK)"
echo ""
echo "📦 Package name: com.example.$PROJECT_NAME"
echo "📱 Display name: $DISPLAY_NAME"
echo ""
echo "🎯 Next steps:"
echo "  1. Build project:    ./gradlew assembleDebug"
echo "  2. Run tests:        ./gradlew test"
echo "  3. Install to device: ./gradlew installDebug"
echo ""
echo "💡 Note: Project name sanitized for Android package naming"
echo "   Original: $PROJECT_NAME_RAW"
echo "   Package:  $PROJECT_NAME"
echo ""
