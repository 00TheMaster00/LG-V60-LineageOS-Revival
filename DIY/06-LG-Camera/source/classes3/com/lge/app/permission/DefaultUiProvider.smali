.class public Lcom/lge/app/permission/DefaultUiProvider;
.super Ljava/lang/Object;
.source "DefaultUiProvider.java"

# interfaces
.implements Lcom/lge/app/permission/GuideUiProvider;


# direct methods
.method public constructor <init>()V
    .registers 1

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public getAppIcon(Landroid/content/Context;)Landroid/graphics/drawable/Drawable;
    .registers 2

    const/4 p0, 0x0

    return-object p0
.end method

.method public getAppName(Landroid/content/Context;[Ljava/lang/String;)Ljava/lang/CharSequence;
    .registers 3

    const-string p0, ""

    return-object p0
.end method

.method public getDisabledFeatures(Landroid/content/Context;[Ljava/lang/String;)Ljava/lang/CharSequence;
    .registers 3

    const-string p0, ""

    return-object p0
.end method

.method public getFullMessageForRequestingPermissions(Landroid/content/Context;[Ljava/lang/String;)Ljava/lang/CharSequence;
    .registers 3

    const-string p0, ""

    return-object p0
.end method

.method public getReasonForRequestingPermissions(Landroid/content/Context;[Ljava/lang/String;)Ljava/lang/CharSequence;
    .registers 3

    const-string p0, ""

    return-object p0
.end method

.method public getRequestPermissionsActivity()Ljava/lang/Class;
    .registers 2

    const/4 v0, 0x0

    return-object v0
.end method
