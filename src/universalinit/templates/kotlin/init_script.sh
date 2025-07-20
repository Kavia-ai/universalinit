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
# Build speed optimizations
org.gradle.jvmargs=-Xmx4g -XX:+UseG1GC -XX:MaxMetaspaceSize=1g -Dfile.encoding=UTF-8 -XX:+UseStringDeduplication
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.workers.max=6

# Kotlin optimizations
kotlin.compiler.execution.strategy=in-process
kotlin.incremental=true
kotlin.incremental.android=true

# Android build optimizations
android.useAndroidX=true
android.debug.testCoverageEnabled=false
android.nonTransitiveRClass=true
android.nonFinalResIds=true
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

# Create gradlew.bat for Windows
cat > "gradlew.bat" << 'EOF'
@rem
@rem Copyright 2015 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      https://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@rem

@if "%DEBUG%" == "" @echo off
@rem ##########################################################################
@rem
@rem  Gradle startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

@rem Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS="-Xmx64m" "-Xms64m"

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if "%ERRORLEVEL%" == "0" goto execute

echo.
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto execute

echo.
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.

goto fail

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\gradle\wrapper\gradle-wrapper.jar


@rem Execute Gradle
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% "-Dorg.gradle.appname=%APP_BASE_NAME%" -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*

:end
@rem End local scope for the variables with windows NT shell
if "%ERRORLEVEL%"=="0" goto mainEnd

:fail
rem Set variable GRADLE_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd.exe /c_ return code!
if not ""=="%GRADLE_EXIT_CONSOLE%" exit 1
exit /b 1

:mainEnd
if "%OS%"=="Windows_NT" endlocal

:omega
EOF

# Download Gradle wrapper jar - improved method with better error handling
echo "Downloading gradle-wrapper.jar..."
mkdir -p gradle/wrapper

# Try multiple download methods
download_success=false

# Try curl first
if command -v curl > /dev/null; then
    if curl -L --retry 3 --retry-delay 2 -o "gradle/wrapper/gradle-wrapper.jar" \
        "https://raw.githubusercontent.com/gradle/gradle/master/gradle/wrapper/gradle-wrapper.jar"; then
        download_success=true
    else
        echo "Warning: curl download failed, trying alternative methods..."
    fi
fi

# Try wget if curl failed
if [ "$download_success" = false ] && command -v wget > /dev/null; then
    if wget -O "gradle/wrapper/gradle-wrapper.jar" \
        "https://raw.githubusercontent.com/gradle/gradle/master/gradle/wrapper/gradle-wrapper.jar"; then
        download_success=true
    else
        echo "Warning: wget download failed, trying alternative source..."
    fi
fi

# Try alternative download source
if [ "$download_success" = false ]; then
    if command -v curl > /dev/null; then
        if curl -L --retry 3 -o "gradle/wrapper/gradle-wrapper.jar" \
            "https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-wrapper.jar"; then
            download_success=true
        fi
    elif command -v wget > /dev/null; then
        if wget -O "gradle/wrapper/gradle-wrapper.jar" \
            "https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-wrapper.jar"; then
            download_success=true
        fi
    fi
fi

# Check if download succeeded
if [ ! -s "gradle/wrapper/gradle-wrapper.jar" ]; then
    # Last resort: create a minimal wrapper jar from base64-encoded content
    echo "Warning: Failed to download gradle-wrapper.jar. Creating minimal wrapper..."
    echo "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" | base64 -d > "gradle/wrapper/gradle-wrapper.jar"
    download_success=true
fi

# Final check and set permissions
if [ "$download_success" = true ]; then
    chmod 644 "gradle/wrapper/gradle-wrapper.jar"
    echo "Gradle wrapper jar installed successfully."
else
    echo "Error: Could not install gradle-wrapper.jar through any method. Please install manually."
    exit 1
fi

echo "Project created successfully! You can now run the project with:"
echo "./gradlew assembleDebug"
echo "To install to a connected device, run:"
echo "./gradlew installDebug"