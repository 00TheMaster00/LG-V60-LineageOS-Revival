.class public final Lcom/lge/media/CamcorderProfileEx;
.super Ljava/lang/Object;
.source "CamcorderProfileEx.java"


# instance fields
.field public videoBitRate:I


# direct methods
.method private constructor <init>(I)V
    .registers 2

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput p1, p0, Lcom/lge/media/CamcorderProfileEx;->videoBitRate:I

    return-void
.end method

.method public static get(II)Lcom/lge/media/CamcorderProfileEx;
    .registers 4

    const/16 v0, 0x36

    if-ne p1, v0, :cond_6

    const/16 p1, 0xd

    :cond_6
    const/16 v0, 0x271d

    if-eq p1, v0, :cond_19

    const/16 v0, 0x271e

    if-eq p1, v0, :cond_19

    const/16 v0, 0x2721

    if-eq p1, v0, :cond_16

    const/16 v0, 0x2722

    if-ne p1, v0, :cond_1b

    :cond_16
    const/16 p1, 0x7d3

    goto :goto_1b

    :cond_19
    const/16 p1, 0x7d4

    :cond_1b
    :goto_1b
    invoke-static {p0, p1}, Landroid/media/CamcorderProfile;->get(II)Landroid/media/CamcorderProfile;

    move-result-object v0

    if-nez v0, :cond_23

    const/4 v1, 0x0

    return-object v1

    :cond_23
    new-instance v1, Lcom/lge/media/CamcorderProfileEx;

    iget v0, v0, Landroid/media/CamcorderProfile;->videoBitRate:I

    invoke-direct {v1, v0}, Lcom/lge/media/CamcorderProfileEx;-><init>(I)V

    return-object v1
.end method

.method public static getManualSupportedList(IIF)Ljava/lang/String;
    .registers 4

    const-string v0, "NotSupport"

    return-object v0
.end method

.method public static hasProfile(II)Z
    .registers 3

    const/16 v0, 0x36

    if-ne p1, v0, :cond_6

    const/16 p1, 0xd

    :cond_6
    const/16 v0, 0x271d

    if-eq p1, v0, :cond_1b

    const/16 v0, 0x271e

    if-eq p1, v0, :cond_1b

    const/16 v0, 0x2721

    if-eq p1, v0, :cond_1b

    const/16 v0, 0x2722

    if-eq p1, v0, :cond_1b

    invoke-static {p0, p1}, Landroid/media/CamcorderProfile;->hasProfile(II)Z

    move-result v0

    return v0

    :cond_1b
    const/4 v0, 0x1

    return v0
.end method
