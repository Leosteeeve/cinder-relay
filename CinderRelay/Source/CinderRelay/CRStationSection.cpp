#include "CRInterfaceLayout.h"
#include "Blueprint/WidgetTree.h"
#include "Components/NativeWidgetHost.h"
#include "Rendering/DrawElements.h"
#include "Styling/CoreStyle.h"
#include "Styling/WidgetStyle.h"
#include "Widgets/DeclarativeSyntaxSupport.h"
#include "Widgets/SLeafWidget.h"

namespace
{
// An original section through the chapter landmarks. A shared coordinate system
// keeps the crane, Workshop and underground route in proportion at either DPI.
class SCRStationSection final : public SLeafWidget
{
public:
    SLATE_BEGIN_ARGS(SCRStationSection) : _TaskArea(INDEX_NONE) {}
        SLATE_ARGUMENT(FSlateFontInfo, Font)
        SLATE_ARGUMENT(int32, TaskArea)
    SLATE_END_ARGS()

    void Construct(const FArguments& Args)
    {
        Font = Args._Font;
        TaskArea = Args._TaskArea;
        SetCanTick(false);
    }

    FVector2D ComputeDesiredSize(float) const override { return FVector2D(640, 178); }

    int32 OnPaint(const FPaintArgs&, const FGeometry& Geometry, const FSlateRect&,
        FSlateWindowElementList& Out, int32 Layer, const FWidgetStyle& Style, bool) const override
    {
        const FVector2f Size = Geometry.GetLocalSize();
        const float Scale = FMath::Min(Size.X / 640.f, Size.Y / 178.f);
        if (Scale <= 0.f) return Layer;
        const FVector2f Origin = (Size - FVector2f(640, 178) * Scale) * .5f;
        const FLinearColor Ink = Style.GetColorAndOpacityTint();
        const auto Color = [Ink](const TCHAR* Hex) { return FLinearColor::FromSRGBColor(FColor::FromHex(Hex)) * Ink; };
        const FLinearColor Dim = Color(TEXT("566A6C")), Line = Color(TEXT("AEC8C3")), Hot = Color(TEXT("F0B56C"));
        const FLinearColor Mark[] = {TaskArea == 0 ? Hot : Line, TaskArea == 1 ? Hot : Line, TaskArea == 2 ? Hot : Line};
        const auto Frame = Geometry.ToPaintGeometry(FVector2f(640, 178), FSlateLayoutTransform(Scale, Origin));
        FSlateDrawElement::MakeBox(Out, Layer, Frame, FCoreStyle::Get().GetBrush("WhiteBrush"),
            ESlateDrawEffect::None, Color(TEXT("122028F4")));
        const auto Stroke = [&](TArray<FVector2f> Points, FLinearColor Tint, float Width = 1.5f)
        {
            FSlateDrawElement::MakeLines(Out, Layer + 1, Frame, MoveTemp(Points), ESlateDrawEffect::None, Tint, true, Width);
        };

        // Rails descend beneath the Workshop. The crane load, sawtooth roof and
        // relay instrument racks are distinct even with the colour removed.
        Stroke({{18,102},{214,102},{246,102},{350,102},{420,136},{622,136}}, Line, 2);
        Stroke({{18,107},{212,107}}, Dim);
        for (int32 X = 24; X < 210; X += 14)
            Stroke({{float(X),107},{float(X - 4),113}}, Dim);
        Stroke({{36,98},{51,35},{155,35},{173,98}}, Mark[0], 2);
        Stroke({{46,98},{61,46},{148,46},{162,98}}, Mark[0]);
        Stroke({{27,35},{27,25},{170,25},{170,35},{27,35}}, Mark[0], 2);
        for (int32 X = 32; X < 157; X += 24)
            Stroke({{float(X),35},{float(X+11),25},{float(X+22),35}}, Dim);
        Stroke({{93,36},{93,61},{89,67},{95,70},{102,64}}, Mark[0]);
        Stroke({{95,70},{75,80},{116,80},{95,70}}, Mark[0]);
        Stroke({{75,80},{75,94},{116,94},{116,80}}, Mark[0], 2);

        Stroke({{230,99},{230,65},{271,46},{271,61},{310,44},{310,61},{350,44},{350,100}}, Mark[1], 2);
        Stroke({{238,73},{342,73}}, Dim);
        for (int32 X = 241; X < 332; X += 31)
            Stroke({{float(X),98},{float(X),81},{float(X+19),81},{float(X+19),98}}, Mark[1]);
        Stroke({{317,54},{317,24},{325,24},{325,51}}, Mark[1]);
        Stroke({{336,49},{336,33},{341,33},{341,47}}, Dim);

        Stroke({{386,100},{411,100},{421,86},{600,86},{612,98},{620,98}}, Dim);
        Stroke({{425,132},{425,100},{435,93},{589,93},{599,102},{599,132}}, Mark[2], 2);
        for (int32 X = 444; X <= 552; X += 36)
        {
            Stroke({{float(X),133},{float(X),102},{float(X+22),102},{float(X+22),133}}, Mark[2]);
            Stroke({{float(X+5),110},{float(X+17),110}}, Dim);
        }
        Stroke({{471,85},{471,63},{496,63},{496,85}}, Mark[2]);
        Stroke({{483,61},{483,27}}, Mark[2]);
        Stroke({{474,40},{492,40}}, Mark[2]);
        Stroke({{478,34},{488,34}}, Mark[2]);

        const TCHAR* Names[] = {TEXT("RAIL YARD"), TEXT("WORKSHOP"), TEXT("RELAY BUNKER")};
        const float Left[] = {22, 232, 425};
        for (int32 I = 0; I < 3; ++I)
        {
            const FVector2f LabelOrigin = Origin + Scale * FVector2f(Left[I], 144);
            const auto LabelFrame = Geometry.ToPaintGeometry(FVector2f(180, 30), FSlateLayoutTransform(Scale, LabelOrigin));
            FSlateDrawElement::MakeText(Out, Layer + 2, LabelFrame, FString(Names[I]), Font, ESlateDrawEffect::None, Mark[I]);
            if (I == TaskArea)
                Stroke({{Left[I]-9,148},{Left[I]-9,163}}, Hot, 3);
        }
        return Layer + 2;
    }

private:
    FSlateFontInfo Font;
    int32 TaskArea = INDEX_NONE;
};
}

UWidget* CRInterfaceLayout::StationSection(UWidgetTree* Tree, UObject* Font, int32 TaskArea, FName Name)
{
    auto* Host = Tree->ConstructWidget<UNativeWidgetHost>(UNativeWidgetHost::StaticClass(), Name);
    Host->SetVisibility(ESlateVisibility::HitTestInvisible);
    const FSlateFontInfo LabelFont = Font ? FSlateFontInfo(Font, 15) : FCoreStyle::GetDefaultFontStyle("Regular", 15);
    Host->SetContent(SNew(SCRStationSection).Font(LabelFont).TaskArea(TaskArea));
    return Host;
}
