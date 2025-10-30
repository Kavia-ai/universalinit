/*
 * Minimal Android TV MainActivity for Kavia universalinit template.
 * Provides a simple starting point that launches on Android TV with the LEANBACK_LAUNCHER.
 */

package com.android.tv.classics

import android.app.Activity
import android.os.Bundle

/**
 * PUBLIC_INTERFACE
 * Entry point Activity for the Android TV application.
 * This minimal activity sets a simple layout and ensures the app launches from the TV launcher.
 */
class MainActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Render a minimal UI defined in res/layout/activity_main.xml
        setContentView(R.layout.activity_main)
    }
}
