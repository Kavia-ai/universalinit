#!/bin/bash

# Check if project name is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 ProjectName [--min-sdk SDK_VERSION] [--target-sdk SDK_VERSION] [--gradle-version VERSION]"
    echo "Example: $0 MyAwesomeApp --min-sdk 26 --gradle-version 8.12"
    exit 1
fi

# Get project name from first argument and remove it from args array
PROJECT_NAME="$1"
shift

# Convert project name to package name (lowercase, remove spaces and special chars)
PACKAGE_NAME="com.example.$(echo ${PROJECT_NAME} | tr '[:upper:]' '[:lower:]' | sed 's/[^a-zA-Z0-9]//g')"

# Default values - updated for new environment
MIN_SDK=24
TARGET_SDK=35
COMPILE_SDK=35
GRADLE_VERSION="8.12"

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

echo "Creating Android project with:"
echo "Project Name: $PROJECT_NAME"
echo "Package Name: $PACKAGE_NAME"
echo "Min SDK: $MIN_SDK"
echo "Target SDK: $TARGET_SDK"
echo "Gradle Version: $GRADLE_VERSION"
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

# Create settings.gradle
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

# Create top-level build.gradle
cat > "build.gradle.kts" << EOF
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:8.7.1")
    }
}
EOF



# Create app/build.gradle
cat > "app/build.gradle.kts" << EOF
plugins {
    id("com.android.application")
}

android {
    namespace = "${PACKAGE_NAME}"
    compileSdk = ${COMPILE_SDK}
    
    buildFeatures {
        buildConfig = true
    }
    
    defaultConfig {
        applicationId = "${PACKAGE_NAME}"
        minSdk = ${MIN_SDK}
        targetSdk = ${TARGET_SDK}
        versionCode = 1
        versionName = "1.0"
        
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.constraintlayout:constraintlayout:2.2.0")
    implementation("androidx.core:core:1.15.0")
    
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.6.1")
}
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
        android:theme="@style/Theme.AppCompat.Light.DarkActionBar">
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

# Create MainActivity.java
cat > "app/src/main/java/$(echo ${PACKAGE_NAME} | tr '.' '/')/MainActivity.java" << EOF
package ${PACKAGE_NAME};

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
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
        android:text="Hello World!"
        android:textSize="18sp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
EOF

# Create gradle.properties
cat > "gradle.properties" << EOF
# Build speed optimizations
org.gradle.jvmargs=-Xmx4g -XX:+UseG1GC -XX:MaxMetaspaceSize=1g -Dfile.encoding=UTF-8 -XX:+UseStringDeduplication
org.gradle.daemon=false
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.workers.max=6
org.gradle.vfs.watch=false

# Kotlin optimizations
kotlin.compiler.execution.strategy=in-process
kotlin.incremental=true
kotlin.incremental.android=true

# Android build optimizations
android.useAndroidX=true
android.debug.testCoverageEnabled=false
android.nonTransitiveRClass=true
android.nonFinalResIds=true
android.enableJetifier=true

# NDK
android.ndkVersion=27.3.13750724
EOF

# Create strings.xml
cat > "app/src/main/res/values/strings.xml" << EOF
<resources>
    <string name="app_name">${PROJECT_NAME}</string>
</resources>
EOF

# Create proguard-rules.pro
cat > "app/proguard-rules.pro" << EOF
# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# If your project uses WebView with JS, uncomment the following
# and specify the fully qualified class name to the JavaScript interface
# class:
#-keepclassmembers class fqcn.of.javascript.interface.for.webview {
#   public *;
#}

# Uncomment this to preserve the line number information for
# debugging stack traces.
#-keepattributes SourceFile,LineNumberTable

# If you keep the line number information, uncomment this to
# hide the original source file name.
#-renamesourcefileattribute SourceFile
EOF

# Use Gradle to generate the wrapper instead of manual download
echo "Generating Gradle wrapper..."
if command -v gradle >/dev/null 2>&1; then
    gradle wrapper --gradle-version=${GRADLE_VERSION} --no-daemon || true
    # If gradle wrapper command did not create the script, fall back
    if [ ! -f "gradlew" ]; then
        echo "Gradle wrapper generation failed or gradle version < ${GRADLE_VERSION} not downloaded, falling back to manual wrapper creation."
        USE_FALLBACK=true
    fi
else
    echo "Warning: Gradle not found in PATH. You may need to run 'gradle wrapper' manually."
    echo "Creating basic gradlew scripts as fallback..."
    # Create gradle-wrapper.properties for the fallback
    mkdir -p "gradle/wrapper"
    cat > "gradle/wrapper/gradle-wrapper.properties" << EOF_PROP
    distributionBase=GRADLE_USER_HOME
    distributionPath=wrapper/dists
    distributionUrl=https\://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip
    networkTimeout=10000
    validateDistributionUrl=true
    zipStoreBase=GRADLE_USER_HOME
    zipStorePath=wrapper/dists
EOF_PROP
    
    # Create gradlew as fallback
    cat > "gradlew" << 'EOF'
#!/bin/sh

# Gradle start script for UN*X

# Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
DEFAULT_JVM_OPTS='"-Xmx64m" "-Xms64m"'

# Use the maximum available, or set MAX_FD != -1 to use that value.
MAX_FD="maximum"

warn () {
    echo "$*"
}

die () {
    echo
    echo "$*"
    echo
    exit 1
}

# OS specific support (must be 'true' or 'false').
cygwin=false
msys=false
darwin=false
nonstop=false
case "`uname`" in
  CYGWIN* )
    cygwin=true
    ;;
  Darwin* )
    darwin=true
    ;;
  MINGW* )
    msys=true
    ;;
  NONSTOP* )
    nonstop=true
    ;;
esac

CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar

# Determine the Java command to use to start the JVM.
if [ -n "$JAVA_HOME" ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
        # IBM's JDK on AIX uses strange locations for the executables
        JAVACMD="$JAVA_HOME/jre/sh/java"
    else
        JAVACMD="$JAVA_HOME/bin/java"
    fi
    if [ ! -x "$JAVACMD" ] ; then
        die "ERROR: JAVA_HOME is set to an invalid directory: $JAVA_HOME

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
else
    JAVACMD="java"
    which java >/dev/null 2>&1 || die "ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
fi

# Increase the maximum file descriptors if we can.
if [ "$cygwin" = "false" -a "$darwin" = "false" -a "$nonstop" = "false" ] ; then
    MAX_FD_LIMIT=`ulimit -H -n`
    if [ $? -eq 0 ] ; then
        if [ "$MAX_FD" = "maximum" -o "$MAX_FD" = "max" ] ; then
            MAX_FD="$MAX_FD_LIMIT"
        fi
        ulimit -n $MAX_FD
        if [ $? -ne 0 ] ; then
            warn "Could not set maximum file descriptor limit: $MAX_FD"
        fi
    else
        warn "Could not query maximum file descriptor limit: $MAX_FD_LIMIT"
    fi
fi

# For Darwin, add options to specify how the application appears in the dock
if [ "$darwin" = "true" ]; then
    GRADLE_OPTS="$GRADLE_OPTS \"-Xdock:name=Gradle\" \"-Xdock:icon=$APP_HOME/media/gradle.icns\""
fi

# For Cygwin or MSYS, switch paths to Windows format before running java
if [ "$cygwin" = "true" -o "$msys" = "true" ] ; then
    APP_HOME=`cygpath --path --mixed "$APP_HOME"`
    CLASSPATH=`cygpath --path --mixed "$CLASSPATH"`
    
    JAVACMD=`cygpath --unix "$JAVACMD"`

    # We build the pattern for arguments to be converted via cygpath
    ROOTDIRSRAW=`find -L / -maxdepth 1 -mindepth 1 -type d 2>/dev/null`
    SEP=""
    for dir in $ROOTDIRSRAW ; do
        ROOTDIRS="$ROOTDIRS$SEP$dir"
        SEP="|"
    done
    OURCYGPATTERN="(^($ROOTDIRS))"
    # Add a user-defined pattern to the cygpath arguments
    if [ "$GRADLE_CYGPATTERN" != "" ] ; then
        OURCYGPATTERN="$OURCYGPATTERN|($GRADLE_CYGPATTERN)"
    fi
    # Now convert the arguments - kludge to limit ourselves to /bin/sh
    i=0
    for arg in "$@" ; do
        CHECK=`echo "$arg"|egrep -c "$OURCYGPATTERN" -`
        CHECK2=`echo "$arg"|egrep -c "^-"`                                 ### Determine if an option

        if [ $CHECK -ne 0 ] && [ $CHECK2 -eq 0 ] ; then                    ### Added a condition
            eval `echo args$i`=`cygpath --path --ignore --mixed "$arg"`
        else
            eval `echo args$i`="\"$arg\""
        fi
        i=`expr $i + 1`
    done
    case $i in
        0) set -- ;;
        1) set -- "$args0" ;;
        2) set -- "$args0" "$args1" ;;
        3) set -- "$args0" "$args1" "$args2" ;;
        4) set -- "$args0" "$args1" "$args2" "$args3" ;;
        5) set -- "$args0" "$args1" "$args2" "$args3" "$args4" ;;
        6) set -- "$args0" "$args1" "$args2" "$args3" "$args4" "$args5" ;;
        7) set -- "$args0" "$args1" "$args2" "$args3" "$args4" "$args5" "$args6" ;;
        8) set -- "$args0" "$args1" "$args2" "$args3" "$args4" "$args5" "$args6" "$args7" ;;
        9) set -- "$args0" "$args1" "$args2" "$args3" "$args4" "$args5" "$args6" "$args7" "$args8" ;;
    esac
fi

# Escape application args
save () {
    for i do printf %s\\n "$i" | sed "s/'/'\\\\''/g;1s/^/'/;\$s/\$/' \\\\/" ; done
    echo " "
}
APP_ARGS=`save "$@"`

# Collect all arguments for the java command
set -- $DEFAULT_JVM_OPTS $JAVA_OPTS $GRADLE_OPTS \
        -classpath "\"$CLASSPATH\"" \
        org.gradle.wrapper.GradleWrapperMain \
        "$APP_ARGS"

exec "$JAVACMD" "$@"
EOF
    chmod +x "gradlew"

    # Try to download gradle-wrapper.jar as fallback
    echo "Attempting to download gradle-wrapper.jar..."
    curl -L -o "gradle/wrapper/gradle-wrapper.jar" \
        "https://github.com/gradle/gradle/raw/v${GRADLE_VERSION}/gradle/wrapper/gradle-wrapper.jar" || \
    curl -L -o "gradle/wrapper/gradle-wrapper.jar" \
        "https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar"
    
    # Verify the wrapper jar was downloaded correctly
    if [ ! -s "gradle/wrapper/gradle-wrapper.jar" ]; then
        echo "Warning: Failed to download gradle-wrapper.jar. You may need to run 'gradle wrapper' manually."
    fi
fi