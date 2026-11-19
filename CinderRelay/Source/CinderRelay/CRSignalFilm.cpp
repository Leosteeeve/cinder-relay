#include "CRSignalFilm.h"
#include "CRAudioSettingsSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Brushes/SlateColorBrush.h"
#include "Components/AudioComponent.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/NativeWidgetHost.h"
#include "Components/TextBlock.h"
#include "Framework/Application/SlateApplication.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Rendering/DrawElements.h"
#include "Rendering/SlateRenderer.h"
#include "Styling/CoreStyle.h"
#include "Widgets/DeclarativeSyntaxSupport.h"
#include "Widgets/SLeafWidget.h"

namespace
{
enum class EPlate { City, Yard, Hands, Receiver, Floodplain };
struct FCut
{
    EPlate Picture;
    const TCHAR* Heading;
    const TCHAR* Caption;
    const TCHAR* Cue;
    float Pitch;
};
const FCut Opening[] = {
    {EPlate::City, TEXT("The Quieting"), TEXT("Decades ago, the world's infrastructure fell silent."), TEXT("BusEnergize"), .58f},
    {EPlate::Hands, TEXT("2118   /   Elias Venn"), TEXT("Elias Venn is a mechanical repair technician."), TEXT("FeedIn"), .76f},
    {EPlate::Yard, TEXT("The Dead Station"), TEXT("Beyond the rail yard, a light still burns in the maintenance Workshop."), TEXT("HoistLift"), .65f},
    {EPlate::Receiver, TEXT("Relay Nine"), TEXT("A replacement power module could bring the underground relay back online."), TEXT("InterlockTravel"), .74f}
};
const FCut Recap[] = {
    {EPlate::Yard, TEXT("The Dead Station"), TEXT("Elias crossed the abandoned rail yard and reached the Workshop."), TEXT("HoistLift"), .78f},
    {EPlate::Hands, TEXT("The Workshop"), TEXT("He recovered a power module and carried it below the station."), TEXT("FeedIn"), .92f},
    {EPlate::Receiver, TEXT("Relay Nine"), TEXT("The terminal read MERIDIAN. A broken carrier tone came back."), TEXT("BusEnergize"), .92f},
    {EPlate::Floodplain, TEXT("Echo Crossing"), TEXT("The line crosses the floodplain here. Find which aerial caught the return."), TEXT("Confirm"), .77f}
};
constexpr float OpeningShotTime = 5.6f, RecapShotTime = 5.1f;
constexpr float FilmW = 1600, FilmH = 680;
const FColor Ink(18,27,31), Dark(30,45,49), Teal(72,97,95), Paper(203,204,174), Brass(223,157,85);

// A batched cut-paper illustration. All shapes are original chapter art. World
// coordinates, parallax and lighting are evaluated only while the film is open.
class FPlateCanvas
{
public:
    FPlateCanvas(const FGeometry& Geometry, float InPhase)
        : Transform(Geometry.GetAccumulatedRenderTransform()), Phase(InPhase)
    {
        const FVector2f Size = Geometry.GetLocalSize();
        Scale = FMath::Max(Size.X / FilmW, Size.Y / FilmH);
        Origin = (Size - Scale * FVector2f(FilmW, FilmH)) * .5f;
        Verts.Reserve(4500);
        Indices.Reserve(6600);
    }
    void Flush(FSlateWindowElementList& List, int32 Layer)
    {
        const auto& Brush = *FCoreStyle::Get().GetBrush("WhiteBrush");
        auto Handle = FSlateApplication::Get().GetRenderer()->GetResourceHandle(Brush);
        FSlateDrawElement::MakeCustomVerts(List, Layer, Handle, Verts, Indices, nullptr, 0, 0);
    }
    void Quad(FVector2f A, FVector2f B, FVector2f C, FVector2f D, FColor Top, FColor Bottom)
    {
        const SlateIndex First = static_cast<SlateIndex>(Verts.Num());
        Vertex(A, Top); Vertex(B, Top); Vertex(C, Bottom); Vertex(D, Bottom);
        Indices.Append({First, SlateIndex(First+1), SlateIndex(First+2), First, SlateIndex(First+2), SlateIndex(First+3)});
    }
    void Rect(float X,float Y,float W,float H,FColor C)
    { Quad({X,Y},{X+W,Y},{X+W,Y+H},{X,Y+H},C,C); }
    void Sky(FColor Top,FColor Bottom)
    { Quad({-400,-180},{2000,-180},{2000,780},{-400,780},Top,Bottom); }
    void Rod(FVector2f A, FVector2f B, float W, FColor C)
    {
        const FVector2f Direction = (B-A).GetSafeNormal() * (W*.5f);
        const FVector2f N(-Direction.Y,Direction.X);
        Quad(A+N,B+N,B-N,A-N,C,C);
    }
    void Oval(float X,float Y,float W,float H,FColor Color)
    {
        constexpr int32 Sides = 48;
        const SlateIndex Center = static_cast<SlateIndex>(Verts.Num()); Vertex({X,Y},Color);
        for (int32 I=0; I<=Sides; ++I)
        {
            const float A=I*(2.f*PI/Sides);
            Vertex({X+FMath::Cos(A)*W,Y+FMath::Sin(A)*H},Color);
            if (I) Indices.Append({Center,SlateIndex(Center+I),SlateIndex(Center+I+1)});
        }
    }
    void Beam(FVector2f A, FVector2f B, FVector2f C, FColor Near, FColor Far)
    { Quad(A,A,B,C,Near,Far); }
    void Dust(FColor Color)
    {
        for(int32 I=0;I<45;++I)
        {
            const float X=FMath::Fmod(I*197.f+122+Phase*(24+(I%7)*5),1650.f);
            const float Y=FMath::Fmod(I*97.f+95-Phase*(13+I%5),625.f);
            Rect(X,Y,1.6f+I%3,1.5f,Color);
        }
    }
    void Pylon(float X, float Ground, float H, FColor C)
    {
        const FVector2f Top(X,Ground-H);
        Rod({X-H*.21f,Ground},Top,4,C); Rod(Top,{X+H*.21f,Ground},4,C);
        for(int32 I=1;I<=4;++I)
        {
            const float T=I/5.f, Span=H*T*.21f, Next=H*(T+.2f)*.21f, Y=Ground-H+T*H;
            Rod({X-Span,Y},{X+Next,Y+H*.2f},2.6f,C);
            Rod({X+Span,Y},{X-Next,Y+H*.2f},2.6f,C);
        }
        for(int32 I=0;I<2;++I)
        {
            const float Y=Ground-H+H*(.15f+.13f*I), Arm=H*(.22f+.05f*I);
            Rod({X-Arm,Y},{X+Arm,Y},4,C); Rod({X-Arm,Y},{X,Y+H*.09f},2,C); Rod({X+Arm,Y},{X,Y+H*.09f},2,C);
        }
    }
    void City()
    {
        Sky({58,75,86},{219,157,110});
        Oval(1130-Phase*10,185,112,112,{224,171,125});
        for(int32 Band=0;Band<3;++Band)
        {
            const FColor C[]={{115,118,112},{77,90,92},{47,64,68}};
            for(int32 I=0;I<20;++I)
            {
                const float X=I*101.f-105-Band*15-Phase*(14+Band*24);
                const float H=45+((I*113+Band*67)%170), Y=430+Band*49-H;
                Rect(X,Y,65.f+(I*23)%47,H+140,C[Band]);
                Rect(X+8,Y-10,26,16,C[Band]);
                if(I%4==0) Rod({X+28,Y},{X+28,Y-33},2,C[Band]);
                for(int32 N=0; N<5; ++N)
                    if ((N+I)%4!=0 && Phase<.92f-((I*11+N*5)%17)*.035f)
                        Rect(X+9+(N%3)*13,Y+18+(N/3)*26,6,3,{215,166,103});
            }
        }
        Pylon(320-Phase*100,670,510,Ink);
        Pylon(1430-Phase*70,650,380,Dark);
        for(int32 I=0;I<3;++I)
        {
            const float Y=234+23*I, Drift=Phase*65;
            Rod({-100,Y+8},{211-Drift,Y},3,Dark);
            FVector2f Last(211-Drift,Y);
            for(int32 J=1;J<=16;++J)
            {
                const float T=J/16.f; FVector2f P(211-Drift+1130*T,Y+74*T+95*FMath::Sin(PI*T));
                Rod(Last,P,2.7f,Dark); Last=P;
            }
        }
        Quad({-30,591},{1640,560},{1640,740},{-30,740},Ink,Ink);
        Dust({220,178,130,110});
    }
    void Yard()
    {
        Sky({44,71,78},{200,164,121});
        Oval(1160-Phase*16,254,81,81,{234,183,130});
        for(int32 I=0;I<12;++I)
        {
            float X=I*167.f-60-19*Phase, Y=352-(I*31)%67;
            Quad({X,Y+18},{X+79,Y},{X+152,Y+18},{X+152,490},Teal,Teal);
            Rect(X,Y+18,152,185,Teal);
        }
        const float Drift=Phase*49;
        Quad({544-Drift,354},{745-Drift,274},{1146-Drift,355},{525-Drift,365},Dark,Dark);
        Rect(565-Drift,360,565,171,Dark);
        for(int32 I=0;I<12;++I) Rod({590.f+I*43-Drift,368},{590.f+I*43-Drift,502},3,Teal);
        Rect(914-Drift,394,103,117,Ink); Rect(922-Drift,399,85,4,Brass);
        Beam({965-Drift,399},{1095-Drift,539},{860-Drift,529},{246,179,103,100},{246,179,103,0});
        Quad({-100,500},{1740,473},{1740,780},{-100,780},{59,61,58},Ink);
        for (int32 I=0;I<10;++I)
        {
            const float Depth=(I+1)*.10f, Y=479+Depth*Depth*240;
            Rod({784-Depth*670,Y},{851+Depth*410,Y-Depth*11},2+Depth*6,{101,98,82});
        }
        for(int32 I=0;I<4;++I)
            Rod({790.f+I*19,480},{-15.f+I*478-Phase*63,730},4,{167,155,122});
        const float Shift=Phase*83;
        Rod({-22-Shift,525},{96-Shift,140},20,Ink); Rod({426-Shift,497},{361-Shift,140},16,Ink);
        Rect(-20-Shift,100,500,14,Ink); Rect(-20-Shift,137,500,10,Ink);
        for(int32 I=0;I<8;++I) Rod({I*64.f-Shift,138},{34+I*64.f-Shift,111},6,Ink);
        Rod({275-Shift,140},{275-Shift,248},3,Ink);
        Rod({275-Shift,248},{224-Shift,277},3,Ink); Rod({275-Shift,248},{318-Shift,277},3,Ink);
        Rect(216-Shift,276,110,43,Dark);
        for(int32 I=0;I<7;++I) Rect(219+I*15.f-Shift,282,3,34,Teal);
        Dust({228,190,132,120});
    }
    void Hands()
    {
        Sky({22,39,45},{89,104,99});
        for(int32 I=0;I<10;++I) Rect(float(I*190)-Phase*18,0,13,506,{41,62,65});
        const float LightX=1090-Phase*34;
        Beam({LightX,42},{1440,590},{468,590},{231,190,131,120},{231,190,131,0});
        Rect(LightX-72,35,144,7,Brass);
        Quad({-100,485},{1710,437},{1710,723},{-100,723},{72,80,72},Ink);
        for(int32 I=0;I<7;++I) Rod({-40,509.f+I*26},{1690,462.f+I*26},1.8f,Dark);
        const float Lift=FMath::Sin(Phase*PI)*23;
        // The power module passes from a gloved palm to the fixture.
        const float X=828+Phase*67, Y=338-Lift;
        Oval(X+18,486,194,18,{41,52,49});
        Rect(X-93,Y-44,181,113,Ink);
        Quad({X-93,Y-44},{X-61,Y-65},{X+113,Y-65},{X+88,Y-44},Paper,Teal);
        Quad({X+88,Y-44},{X+113,Y-65},{X+113,Y+42},{X+88,Y+69},Teal,Dark);
        Rect(X-78,Y-29,143,71,Teal);
        for(int32 I=0;I<8;++I) Rect(X-68+I*15,Y-14,7,43,Dark);
        Rect(X-78,Y+49,66,5,Brass);
        for(int32 I=0;I<3;++I) Rect(X-54+I*42,Y-74,17,13,Brass);
        const float Glove=Phase*61;
        Quad({-130,676},{326+Glove,390-Lift},{435+Glove,456-Lift},{172,735},Dark,Ink);
        Quad({294+Glove,399-Lift},{390+Glove,348-Lift},{482+Glove,424-Lift},{421+Glove,471-Lift},Teal,Dark);
        Quad({385+Glove,350-Lift},{511+Glove,291-Lift},{673+Glove,340-Lift},{472+Glove,427-Lift},Dark,Ink);
        for(int32 I=0;I<4;++I)
        {
            const float A=I*16.f;
            Rod({533+Glove+A,335-Lift+A},{672+Glove+A,351-Lift+A},23,Dark);
            Rod({672+Glove+A,351-Lift+A},{723+Glove+A,337-Lift+A},17,Ink);
        }
        Rod({492+Glove,321-Lift},{543+Glove,269-Lift},28,Dark);
        Rod({543+Glove,269-Lift},{622+Glove,293-Lift},21,Dark);
        Dust({213,201,160,110});
    }
    void Receiver(bool Powered)
    {
        Sky({31,54,59},{91,103,92});
        for(int32 I=0;I<7;++I)
        {
            const float X=I*250.f-43*Phase;
            Rect(X,15,216,660,Dark);
            for(int32 J=0;J<10;++J) Rect(X+14,42.f+J*56,182,5,Teal);
        }
        const float X=819-34*Phase;
        Quad({X-420,94},{X+421,76},{X+438,505},{X-430,523},Ink,Dark);
        Quad({X-377,128},{X+377,113},{X+392,455},{X-388,470},{210,191,141},{126,153,143});
        const FVector2f Center(X,506);
        FVector2f Prev = Center;
        for(int32 I=0;I<=52;++I)
        {
            const float A=PI*(1.20f+.60f*I/52.f), C=FMath::Cos(A), S=FMath::Sin(A);
            const FVector2f Outer=Center+FVector2f(C,S)*324;
            if(I) Rod(Prev,Outer,3,Dark);
            Rod(Outer,Outer-FVector2f(C,S)*(I%4==0?29.f:11.f),I%4==0?3.5f:1.6f,Dark);
            Prev=Outer;
        }
        const float NeedleAngle=PI*(Powered ? 1.26f+.41f*FMath::SmoothStep(0.f,.76f,Phase)+.012f*FMath::Sin(Phase*57) : 1.26f);
        const FVector2f Tip=Center+FVector2f(FMath::Cos(NeedleAngle),FMath::Sin(NeedleAngle))*300;
        Rod(Center,Tip,7,{148,75,45});
        Rect(X-431,464,866,119,Dark);
        for(int32 I=0;I<4;++I) Rect(X-320+I*164,496,111,9,Powered && I < 1+int32(Phase*4) ? Brass : Teal);
        Oval(X,478,34,15,Ink);
        Dust({222,189,137,90});
    }
    void Crossing()
    {
        Sky({54,82,90},{216,173,121});
        Oval(359+Phase*8,229,90,90,{222,175,129});
        for(int32 I=0;I<15;++I)
        {
            float X=I*130.f-Phase*22, Y=367-(I*19)%56;
            Quad({X-90,412},{X,Y},{X+86,Y+11},{X+175,415},Teal,Teal);
        }
        Quad({-120,399},{1740,399},{1740,750},{-120,750},{124,151,144},{46,80,84});
        for(int32 I=0;I<72;++I)
        {
            float X=(I*193)%1680-38+Phase*(6+I%12);
            float Y=417+(I*37)%231;
            Rect(X,Y,15+(I*9)%89,1+I%2,{179,178,145,165});
        }
        Quad({-130,504},{337,454},{574,465},{-100,631},Dark,Ink);
        Quad({925,514},{1422,431},{1730,442},{1710,595},Dark,Ink);
        Pylon(1130-Phase*18,458,204,Dark); Pylon(1405-Phase*22,441,146,Dark);
        Rod({1118-Phase*18,290},{1257,337},2,Dark); Rod({1257,337},{1398-Phase*22,325},2,Dark);
        const float X=366-Phase*68;
        Rect(X-89,364,164,109,Dark);
        Quad({X-107,364},{X-24,322},{X+89,354},{X+80,365},Ink,Ink);
        Rect(X+24,388,26,39,Brass);
        const float Blink=.5f+.5f*FMath::Sin(Phase*PI*4);
        Oval(1130-Phase*18,254,4+Blink*3,4+Blink*3,{237,165,88});
        Dust({209,185,139,90});
    }
private:
    void Vertex(FVector2f P, FColor Color)
    {
        Verts.Add(FSlateVertex::Make<ESlateVertexRounding::Disabled>(Transform,Origin+Scale*P,FVector2f(.5f,.5f),Color));
    }
    FSlateRenderTransform Transform;
    float Phase;
    float Scale = 1;
    FVector2f Origin;
    TArray<FSlateVertex> Verts;
    TArray<SlateIndex> Indices;
};

class SSignalPicture final : public SLeafWidget
{
public:
    SLATE_BEGIN_ARGS(SSignalPicture) : _Recap(false) {}
        SLATE_ARGUMENT(TWeakObjectPtr<UCRSignalFilm>, Film)
        SLATE_ARGUMENT(bool, Recap)
    SLATE_END_ARGS()
    void Construct(const FArguments& A) { Film=A._Film; bRecap=A._Recap; SetCanTick(false); }
    FVector2D ComputeDesiredSize(float) const override { return {FilmW,FilmH}; }
    int32 OnPaint(const FPaintArgs&,const FGeometry& Geo,const FSlateRect&,FSlateWindowElementList& Out,
        int32 Layer,const FWidgetStyle&,bool) const override
    {
        if(!Film.IsValid()) return Layer;
        const float SecondsPerShot=bRecap ? RecapShotTime : OpeningShotTime;
        const float T=Film->GetPlaybackTime();
        const int32 Index=FMath::Clamp(int32(T/SecondsPerShot),0,3);
        const float Phase=FMath::Clamp(T/SecondsPerShot-Index,0.f,1.f);
        FPlateCanvas Canvas(Geo,Phase);
        switch ((bRecap ? Recap[Index] : Opening[Index]).Picture)
        {
        case EPlate::City: Canvas.City(); break;
        case EPlate::Yard: Canvas.Yard(); break;
        case EPlate::Hands: Canvas.Hands(); break;
        case EPlate::Receiver: Canvas.Receiver(bRecap); break;
        case EPlate::Floodplain: Canvas.Crossing(); break;
        }
        Canvas.Flush(Out,Layer);
        const float Fade=1.f-FMath::Clamp(FMath::Min(Phase,1.f-Phase)*SecondsPerShot/.27f,0.f,1.f);
        if(Fade>0) FSlateDrawElement::MakeBox(Out,Layer+1,Geo.ToPaintGeometry(),
            FCoreStyle::Get().GetBrush("WhiteBrush"),ESlateDrawEffect::None,FLinearColor(0.005f,.009f,.012f,Fade));
        return Layer+1;
    }
private:
    TWeakObjectPtr<UCRSignalFilm> Film;
    bool bRecap=false;
};
}

UCRSignalFilm* UCRSignalFilm::Open(APlayerController* Owner, bool bRecap, FSimpleDelegate OnFinished)
{
    if (!IsValid(Owner) || !Owner->IsLocalController()) return nullptr;
    auto* Film=CreateWidget<UCRSignalFilm>(Owner,StaticClass());
    if (!Film) return nullptr;
    Film->bRecapVersion=bRecap;
    Film->WhenFinished=MoveTemp(OnFinished);
    Film->SetIsFocusable(true);
    Film->BuildScreen();
    Film->StartedAt=FPlatformTime::Seconds();
    Film->AddToViewport(1000);
    Film->SetUserFocus(Owner);
    Film->SetKeyboardFocus();
    Film->EnterShot(0);
    return Film;
}

void UCRSignalFilm::BuildScreen()
{
    auto* Root=WidgetTree->ConstructWidget<UCanvasPanel>();
    WidgetTree->RootWidget=Root;
    auto Place=[Root](UWidget* W,FAnchors Anchors,FMargin Margins,int32 Layer=0)
    {
        auto* Slot=Root->AddChildToCanvas(W);
        Slot->SetAnchors(Anchors);
        Slot->SetOffsets(Margins);
        Slot->SetZOrder(Layer);
        return Slot;
    };
    auto* Back=WidgetTree->ConstructWidget<UBorder>();
    Back->SetBrushColor(FLinearColor::FromSRGBColor({12,22,26}));
    Place(Back,FAnchors(0,0,1,1),FMargin(0));
    auto* Host=WidgetTree->ConstructWidget<UNativeWidgetHost>();
    auto SlateArt=SNew(SSignalPicture).Film(TWeakObjectPtr<UCRSignalFilm>(this)).Recap(bRecapVersion);
    Artwork=SlateArt;
    Host->SetContent(SlateArt);
    Host->SetClipping(EWidgetClipping::ClipToBoundsAlways);
    Host->SetVisibility(ESlateVisibility::HitTestInvisible);
    Place(Host,FAnchors(0,.085f,1,.745f),FMargin(0),1);

    // Fonts are already resident when launched from the chapter menu. The core
    // style also supports a direct replay from an isolated runtime fixture.
    const FSoftObjectPath BodyPath(TEXT("/Game/Generated/Phase055/Interface/Fonts/F_CR055_Body.F_CR055_Body"));
    const FSoftObjectPath HeadPath(TEXT("/Game/Generated/Phase055/Interface/Fonts/F_CR055_Title.F_CR055_Title"));
    auto Label=[this,&BodyPath,&HeadPath](const TCHAR* Value,int32 Size,FColor Color,bool Heading)
    {
        auto* T=WidgetTree->ConstructWidget<UTextBlock>();
        auto* Asset=(Heading?HeadPath:BodyPath).ResolveObject();
        T->SetFont(Asset ? FSlateFontInfo(Asset,Size) : FCoreStyle::GetDefaultFontStyle(Heading?"Bold":"Regular",Size));
        T->SetColorAndOpacity(FLinearColor::FromSRGBColor(Color));
        T->SetText(FText::FromString(Value));
        return T;
    };
    auto* Chapter=Label(bRecapVersion?TEXT("CINDER RELAY    /    CHAPTER 02"):TEXT("CINDER RELAY    /    CHAPTER 01"),
        18,{172,193,183},false);
    auto* ChapterSlot=Place(Chapter,FAnchors(.055f,.043f),FMargin(0,0,765,36),2);
    ChapterSlot->SetAlignment({0,.5f});
    auto* Skip=WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(),TEXT("SkipFilm"));
    FButtonStyle ButtonStyle;
    ButtonStyle.SetNormal(FSlateColorBrush(FLinearColor::FromSRGBColor({32,46,48})))
        .SetHovered(FSlateColorBrush(FLinearColor::FromSRGBColor({64,77,72})))
        .SetPressed(FSlateColorBrush(FLinearColor::FromSRGBColor({82,71,50})));
    Skip->SetStyle(ButtonStyle);
    Skip->SetContent(Label(TEXT("Skip   [Tab]"),18,{234,226,208},false));
    Skip->OnClicked.AddDynamic(this,&UCRSignalFilm::FinishFilm);
    auto* SkipSlot=Place(Skip,FAnchors(.945f,.043f),FMargin(0,0,160,44),2);
    SkipSlot->SetAlignment({1,.5f});
    ShotTitle=Label(TEXT(""),38,{237,188,124},true);
    Place(ShotTitle,FAnchors(.055f,.775f,.945f,.89f),FMargin(0),2);
    Caption=Label(TEXT(""),26,{239,237,226},false);
    Caption->SetAutoWrapText(true);
    Place(Caption,FAnchors(.055f,.852f,.945f,.98f),FMargin(0),2);
}

float UCRSignalFilm::GetDuration() const
{
    return bRecapVersion ? UE_ARRAY_COUNT(Recap)*RecapShotTime : UE_ARRAY_COUNT(Opening)*OpeningShotTime;
}

void UCRSignalFilm::EnterShot(int32 Shot)
{
    ActiveShot=Shot;
    const FCut& Cut=bRecapVersion?Recap[Shot]:Opening[Shot];
    ShotTitle->SetText(FText::FromString(Cut.Heading));
    Caption->SetText(FText::FromString(Cut.Caption));
    StopCue();
    auto* Mix=UCRAudioSettingsSubsystem::Get(this);
    if (auto* Wave=Mix ? Mix->GetResidentSound(Cut.Cue) : nullptr)
    {
        Sound=UGameplayStatics::CreateSound2D(this,Wave,.55f,Cut.Pitch);
        if (Sound)
        {
            Sound->bIsUISound=true;
            Sound->Play();
        }
    }
}

void UCRSignalFilm::NativeTick(const FGeometry& Geometry,float Delta)
{
    Super::NativeTick(Geometry,Delta);
    if (bFinished) return;
    Playback=FMath::Clamp(float(FPlatformTime::Seconds()-StartedAt),0.f,GetDuration());
    if (Playback>=GetDuration())
    {
        FinishFilm();
        return;
    }
    const float ShotLength=bRecapVersion?RecapShotTime:OpeningShotTime;
    const int32 Shot=FMath::Clamp(int32(Playback/ShotLength),0,3);
    if (ActiveShot!=Shot) EnterShot(Shot);
    if (auto Art=Artwork.Pin()) Art->Invalidate(EInvalidateWidgetReason::Paint);
}

FReply UCRSignalFilm::NativeOnPreviewKeyDown(const FGeometry&,const FKeyEvent& Event)
{
    const FKey Key=Event.GetKey();
    if (!Event.IsRepeat() && (Key==EKeys::Tab || Key==EKeys::Enter || Key==EKeys::Escape)) FinishFilm();
    return FReply::Handled();
}

void UCRSignalFilm::StopCue()
{
    if (IsValid(Sound)) Sound->Stop();
    Sound=nullptr;
}

void UCRSignalFilm::FinishFilm()
{
    if (bFinished) return;
    bFinished=true;
    auto Callback=MoveTemp(WhenFinished);
    StopCue();
    RemoveFromParent();
    Callback.ExecuteIfBound();
}

void UCRSignalFilm::NativeDestruct()
{
    bFinished=true;
    WhenFinished.Unbind();
    StopCue();
    Artwork.Reset();
    Super::NativeDestruct();
}
