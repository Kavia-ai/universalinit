#!/bin/bash

# Check if project name is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 ProjectName [--min-sdk SDK_VERSION] [--target-sdk SDK_VERSION] [--gradle-version VERSION]"
    echo "Example: $0 MyKotlinApp --min-sdk 26 --gradle-version 8.12"
    exit 1
fi

# Get project name from first argument and remove it from args array
PROJECT_NAME="$1"
shift

# Convert project name to package name (lowercase, remove spaces and special chars)
PACKAGE_NAME="com.example.$(echo ${PROJECT_NAME} | tr '[:upper:]' '[:lower:]' | sed 's/[^a-zA-Z0-9]//g')"

# Create a safe theme name (no dashes, spaces, etc.)
THEME_NAME="AppTheme"

# Default values
MIN_SDK=24
TARGET_SDK=34
COMPILE_SDK=34
GRADLE_VERSION="8.12"
KOTLIN_VERSION="1.9.22"

# Parse remaining command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --min-sdk)
            MIN_SDK="$2"
            shift 2
            ;;
        --target-sdk)
            TARGET_SDK="$2"
            COMPILE_SDK="$2"
            shift 2
            ;;
        --gradle-version)
            GRADLE_VERSION="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

echo "Creating Kotlin Android project with:"
echo "Project Name: $PROJECT_NAME"
echo "Package Name: $PACKAGE_NAME"
echo "Min SDK: $MIN_SDK"
echo "Target SDK: $TARGET_SDK"
echo "Gradle Version: $GRADLE_VERSION"
echo "Kotlin Version: $KOTLIN_VERSION"
echo ""

# Create project directory structure
mkdir -p "app/src/main/java/$(echo ${PACKAGE_NAME} | tr '.' '/')"
mkdir -p "app/src/main/res/layout"
mkdir -p "app/src/main/res/values"
mkdir -p "app/src/main/res/mipmap-mdpi"
mkdir -p "app/src/main/res/mipmap-hdpi"
mkdir -p "app/src/main/res/mipmap-xhdpi"
mkdir -p "app/src/main/res/mipmap-xxhdpi"
mkdir -p "app/src/main/res/mipmap-xxxhdpi"
mkdir -p "gradle/wrapper"

# Create basic launcher icons (1x1 pixel PNG as placeholder)
echo "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAACfklEQVR42u2ZTWgTQRTHf12bbGo/ErWoUFAhFg9+FDzVkwcRQduK9iQignhV9OJJvAjqwYMXEUEQFQ+KJ1FR8SK0IBbxZFHQiqIWLdqU2jRNdjysDTbJZme6M5tAZmCh2X3z9r//e/NmdhYUCoVCoVAoyoXjwDLVxrbxKmCR7+F54lXyEn4+cNTzxHMKvwyYyJ7HVtUGr1IZ/ykqUskjvyJSG77qQrJTJz5/XWPFtbsHgWeAA9wHPgKLgHpgJbAO2AhsA2qBo8AoMMXLZnkfqSwcYAtwCmjiX4wAt4A+oB+YnGFNDfAJGGZXYkZkK/AY2JjnmklgAGgFruZZ0wu0Awu5VeQUsAZZHgA7gdaC8AA3gI0i3pXVKdYVsYMSz3oZGAPGJdYsBR4CS1SfbQvwgGUJzofyv5X8XZG8BFLYxiHgInANuACcANbGnN8jGh7sO9BI/IbmAmeAbuCVIMuTgCXAKYnY1jkwDHSKxpeJu0BdFHgTaMgj/DXwHfgJdBE09fVZ3weBbtmkPghcTpgDWdQBxySr0HbgvIT4fuC+bBeXQRVwDNgvmaIeAE/TVqEG4DzRkzUtOoFDiXKAYPy9Ani7nRSHHeCtwPqPwuuSsohvA9oF1/cA79OoQgeAdYLrLxFsgNrCBSYkxLvAPWBFmgI+GREGPgxcwQKWhbT5sXDGsICvXBTt5rN4ALyXED9CMPZbQ7/Xe7GRd08SblEmiHcl7tKs4bHX60PCYn4CZ4FRwdEpDAPfBMXPB24D87Exwvpd8fPXOkm0iW9XZAoF3hE2YPNX9lf4a9gXUOnCFQqFQqFQKBQKxSz5A6iM6SmxGAW3AAAAAElFTkSuQmCC" | base64 -d > "app/src/main/res/mipmap-mdpi/ic_launcher.png"
echo "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAACfklEQVR42u2ZTWgTQRTHf12bbGo/ErWoUFAhFg9+FDzVkwcRQduK9iQignhV9OJJvAjqwYMXEUEQFQ+KJ1FR8SK0IBbxZFHQiqIWLdqU2jRNdjysDTbJZme6M5tAZmCh2X3z9r//e/NmdhYUCoVCoVAoyoXjwDLVxrbxKmCR7+F54lXyEn4+cNTzxHMKvwyYyJ7HVtUGr1IZ/ykqUskjvyJSG77qQrJTJz5/XWPFtbsHgWeAA9wHPgKLgHpgJbAO2AhsA2qBo8AoMMXLZnkfqSwcYAtwCmjiX4wAt4A+oB+YnGFNDfAJGGZXYkZkK/AY2JjnmklgAGgFruZZ0wu0Awu5VeQUsAZZHgA7gdaC8AA3gI0i3pXVKdYVsYMSz3oZGAPGJdYsBR4CS1SfbQvwgGUJzofyv5X8XZG8BFLYxiHgInANuACcANbGnN8jGh7sO9BI/IbmAmeAbuCVIMuTgCXAKYnY1jkwDHSKxpeJu0BdFHgTaMgj/DXwHfgJdBE09fVZ3weBbtmkPghcTpgDWdQBxySr0HbgvIT4fuC+bBeXQRVwDNgvmaIeAE/TVqEG4DzRkzUtOoFDiXKAYPy9Ani7nRSHHeCtwPqPwuuSsohvA9oF1/cA79OoQgeAdYLrLxFsgNrCBSYkxLvAPWBFmgI+GREGPgxcwQKWhbT5sXDGsICvXBTt5rN4ALyXED9CMPZbQ7/Xe7GRd08SblEmiHcl7tKs4bHX60PCYn4CZ4FRwdEpDAPfBMXPB24D87Exwvpd8fPXOkm0iW9XZAoF3hE2YPNX9lf4a9gXUOnCFQqFQqFQKBQKxSz5A6iM6SmxGAW3AAAAAElFTkSuQmCC" | base64 -d > "app/src/main/res/mipmap-mdpi/ic_launcher_round.png"

# Copy the same placeholder to all resolution directories
for dir in hdpi xhdpi xxhdpi xxxhdpi; do
    cp "app/src/main/res/mipmap-mdpi/ic_launcher.png" "app/src/main/res/mipmap-${dir}/ic_launcher.png"
    cp "app/src/main/res/mipmap-mdpi/ic_launcher_round.png" "app/src/main/res/mipmap-${dir}/ic_launcher_round.png"
done

# Create settings.gradle.kts
cat > "settings.gradle.kts" << EOF
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

rootProject.name = "${PROJECT_NAME}"
include(":app")
EOF

# Create top-level build.gradle.kts
cat > "build.gradle.kts" << EOF
// Top-level build file
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "${KOTLIN_VERSION}" apply false
}
EOF

# Create gradle-wrapper.properties
cat > "gradle/wrapper/gradle-wrapper.properties" << EOF
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

# Create simple gradlew script
cat > "gradlew" << 'EOF'
#!/bin/sh

# Add default JVM options here
DEFAULT_JVM_OPTS="-Xmx64m -Xms64m"

# Determine the project root directory
SCRIPT_DIR=$(dirname "$0")
APP_HOME=$(cd "$SCRIPT_DIR" >/dev/null && pwd)

# Set up classpath
CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar

# Execute Gradle
exec java $DEFAULT_JVM_OPTS \
  -Dorg.gradle.appname=gradlew \
  -classpath "$CLASSPATH" \
  org.gradle.wrapper.GradleWrapperMain "$@"
EOF
chmod +x "gradlew"

# Create app/build.gradle.kts
cat > "app/build.gradle.kts" << EOF
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "${PACKAGE_NAME}"
    compileSdk = ${COMPILE_SDK}

    defaultConfig {
        applicationId = "${PACKAGE_NAME}"
        minSdk = ${MIN_SDK}
        targetSdk = ${TARGET_SDK}
        versionCode = 1
        versionName = "1.0"
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
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = "1.8"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
}
EOF

# Create gradle.properties
cat > "gradle.properties" << EOF
# Project-wide Gradle settings
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
org.gradle.parallel=true
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
EOF

# Create proguard-rules.pro
cat > "app/proguard-rules.pro" << EOF
# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.kts.
EOF

# Create AndroidManifest.xml
cat > "app/src/main/AndroidManifest.xml" << EOF
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/${THEME_NAME}">
        <activity android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
EOF

# Create MainActivity.kt
cat > "app/src/main/java/$(echo ${PACKAGE_NAME} | tr '.' '/')/MainActivity.kt" << EOF
package ${PACKAGE_NAME}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
EOF

# Create activity_main.xml
cat > "app/src/main/res/layout/activity_main.xml" << EOF
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Hello Kotlin World!"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
EOF

# Create strings.xml
cat > "app/src/main/res/values/strings.xml" << EOF
<resources>
    <string name="app_name">${PROJECT_NAME}</string>
</resources>
EOF

# Create themes.xml
cat > "app/src/main/res/values/themes.xml" << EOF
<resources>
    <style name="${THEME_NAME}" parent="Theme.MaterialComponents.DayNight.DarkActionBar">
        <item name="colorPrimary">#6200EE</item>
        <item name="colorPrimaryDark">#3700B3</item>
        <item name="colorAccent">#03DAC5</item>
    </style>
</resources>
EOF

# Create colors.xml
cat > "app/src/main/res/values/colors.xml" << EOF
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>
EOF

# Download Gradle wrapper jar
echo "Downloading gradle-wrapper.jar..."
curl -L -o "gradle/wrapper/gradle-wrapper.jar" \
    "https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar"

# Verify the wrapper jar was downloaded correctly
if [ ! -s "gradle/wrapper/gradle-wrapper.jar" ]; then
    echo "Error: Failed to download gradle-wrapper.jar or file is empty"
    exit 1
fi

echo "Project created successfully! You can now run the project with:"
echo "./gradlew assembleDebug"