#include <jni.h>
#include <stdint.h>

// These are stable bionic loader entry points.  Keeping the declarations here
// avoids depending on a full NDK installation for this one-function shim.
extern "C" void* dlopen(const char* filename, int flags);
extern "C" void* dlsym(void* handle, const char* symbol);

namespace {

constexpr int kRtldNow = 2;

using SetConsumerUsageBits = int (*)(void* surface_texture, uint64_t usage);

}  // namespace

extern "C" JNIEXPORT jint JNICALL
Java_com_lge_camera_util_SurfaceUsageShim_nativeSetConsumerUsage(
        JNIEnv* env, jclass, jobject surface_texture, jlong usage) {
    if (surface_texture == nullptr) {
        return -1;
    }

    jclass surface_texture_class = env->GetObjectClass(surface_texture);
    if (surface_texture_class == nullptr) {
        return -2;
    }

    // Android's own SurfaceTexture JNI stores the native SurfaceTexture pointer
    // in this long field. JNI field access is not subject to hidden-API checks.
    jfieldID native_field =
            env->GetFieldID(surface_texture_class, "mSurfaceTexture", "J");
    if (native_field == nullptr) {
        if (env->ExceptionCheck()) {
            env->ExceptionClear();
        }
        return -3;
    }

    void* native_surface_texture = reinterpret_cast<void*>(
            static_cast<uintptr_t>(env->GetLongField(surface_texture, native_field)));
    if (native_surface_texture == nullptr) {
        return -4;
    }

    // libandroid is an app-accessible NDK library and already depends on
    // libnativedisplay in this ROM. Looking through that handle lets us use the
    // ROM's exact SurfaceTexture implementation without packaging a framework
    // library or replacing any system file.
    void* libandroid = dlopen("libandroid.so", kRtldNow);
    if (libandroid == nullptr) {
        return -5;
    }

    auto set_consumer_usage = reinterpret_cast<SetConsumerUsageBits>(dlsym(
            libandroid,
            "_ZN7android14SurfaceTexture20setConsumerUsageBitsEm"));
    if (set_consumer_usage == nullptr) {
        return -6;
    }

    return set_consumer_usage(native_surface_texture,
                              static_cast<uint64_t>(usage));
}
