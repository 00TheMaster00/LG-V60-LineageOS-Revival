.class public Lcom/lge/display/DisplayManagerHelper;
.super Ljava/lang/Object;
.source "DisplayManagerHelper.java"


# direct methods
.method public constructor <init>(Landroid/content/Context;)V
    .registers 2

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static getMultiDisplayType()I
    .registers 1

    const/4 v0, 0x0

    return v0
.end method

.method public static isMultiDisplayDevice()Z
    .registers 1

    const/4 v0, 0x0

    return v0
.end method


# virtual methods
.method public getCoverDisplayState()I
    .registers 2

    const/4 v0, 0x0

    return v0
.end method

.method public getCoverState()I
    .registers 2

    const/4 v0, 0x0

    return v0
.end method

.method public getSwivelState()I
    .registers 2

    const/4 v0, 0x0

    return v0
.end method

.method public registerSwivelStateCallback(Lcom/lge/display/DisplayManagerHelper$SwivelStateCallback;)V
    .registers 2

    return-void
.end method

.method public unregisterSwivelStateCallback(Lcom/lge/display/DisplayManagerHelper$SwivelStateCallback;)V
    .registers 2

    return-void
.end method
