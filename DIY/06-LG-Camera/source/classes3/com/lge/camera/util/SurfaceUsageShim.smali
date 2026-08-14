.class public final Lcom/lge/camera/util/SurfaceUsageShim;
.super Ljava/lang/Object;
.source "SurfaceUsageShim.java"


# static fields
.field private static sLoaded:Z


# direct methods
.method static constructor <clinit>()V
    .registers 2

    :try_start_0
    const-string v0, "lgcamera_surface_usage"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    const/4 v0, 0x1

    sput-boolean v0, Lcom/lge/camera/util/SurfaceUsageShim;->sLoaded:Z
    :try_end_8
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_8} :catch_9

    goto :goto_12

    :catch_9
    move-exception v0

    const-string v1, "LGCamSurfaceUsage"

    invoke-static {v1, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/Throwable;)I

    const/4 v0, 0x0

    sput-boolean v0, Lcom/lge/camera/util/SurfaceUsageShim;->sLoaded:Z

    :goto_12
    return-void
.end method

.method private constructor <init>()V
    .registers 1

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static apply(Landroid/graphics/SurfaceTexture;)I
    .registers 4

    sget-boolean v0, Lcom/lge/camera/util/SurfaceUsageShim;->sLoaded:Z

    if-nez v0, :cond_e

    const-string p0, "LGCamSurfaceUsage"

    const-string v0, "native shim is unavailable"

    invoke-static {p0, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    const/16 p0, -0x64

    return p0

    :cond_e
    const-wide/32 v1, 0x20900

    invoke-static {p0, v1, v2}, Lcom/lge/camera/util/SurfaceUsageShim;->nativeSetConsumerUsage(Landroid/graphics/SurfaceTexture;J)I

    move-result p0

    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "setConsumerUsageBits(0x20900)="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    const-string v1, "LGCamSurfaceUsage"

    invoke-static {v1, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    return p0
.end method

.method private static native nativeSetConsumerUsage(Landroid/graphics/SurfaceTexture;J)I
.end method
