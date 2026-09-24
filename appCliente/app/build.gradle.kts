plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "uk.app02loveslollipop.mipedido.cliente"
    compileSdk = 34

    defaultConfig {
        applicationId = "uk.app02loveslollipop.mipedido.cliente"
        minSdk = 29
        targetSdk = 34
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
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
    buildFeatures {
        compose = true
    }
}

val accompanistVersion = "0.32.0"
val retrofitVersion = "3.0.0"
val okhttpVersion = "5.2.1"
val gsonVersion = "2.13.2"
val coroutinesVersion = "1.10.2"
val coroutinesCoreVersion = "1.7.1"
val coilVersion = "2.7.0"
val navigationVersion = "2.7.0"
val zxingVersion = "3.5.4"
val cameraVersion = "1.3.0"
val mlkitBarcodeVersion = "17.2.0"
val materialVersion = "1.6.0"
val osmdroidVersion = "6.1.16"

dependencies {

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)

    // Experimental permissions for location
    implementation("com.google.accompanist:accompanist-permissions:$accompanistVersion")

    // Retrofit for API calls
    implementation("com.squareup.retrofit2:retrofit:$retrofitVersion")
    implementation("com.squareup.retrofit2:converter-gson:$retrofitVersion")
    
    // OkHttp for networking
    implementation("com.squareup.okhttp3:okhttp:$okhttpVersion")
    implementation("com.squareup.okhttp3:logging-interceptor:$okhttpVersion")
    
    // Gson for JSON parsing
    implementation("com.google.code.gson:gson:$gsonVersion")
    
    // Coroutines for asynchronous programming
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:$coroutinesVersion")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:$coroutinesCoreVersion")
    
    // Coil for image loading
    implementation("io.coil-kt:coil-compose:$coilVersion")
    
    // Navigation Component
    implementation("androidx.navigation:navigation-compose:$navigationVersion")
    
    // ZXing for QR code generation
    implementation("com.google.zxing:core:$zxingVersion")
    
    // CameraX for camera access
    implementation("androidx.camera:camera-camera2:$cameraVersion")
    implementation("androidx.camera:camera-lifecycle:$cameraVersion")
    implementation("androidx.camera:camera-view:$cameraVersion")
    
    // Google ML Kit for barcode scanning
    implementation("com.google.mlkit:barcode-scanning:$mlkitBarcodeVersion")
    
    implementation("androidx.compose.material:material:$materialVersion")
    
    // OSMDroid for maps
    implementation("org.osmdroid:osmdroid-android:$osmdroidVersion")
    implementation("org.osmdroid:osmdroid-mapsforge:$osmdroidVersion")
    
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}