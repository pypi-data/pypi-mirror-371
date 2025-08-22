"""ImPlot Library"""
from __future__ import annotations
import imgui.implot
import typing
import imgui

__all__ = [
    "AddColorMap",
    "Annotation",
    "Axis",
    "AxisFlags",
    "BarGroupsFlags",
    "BarsFlags",
    "BeginAlignedPlots",
    "BeginDragDropSourceAxis",
    "BeginDragDropSourceItem",
    "BeginDragDropSourcePlot",
    "BeginDragDropTargetAxis",
    "BeginDragDropTargetLegend",
    "BeginDragDropTargetPlot",
    "BeginLegendPopup",
    "BeginPlot",
    "BeginSubplots",
    "Bin",
    "BustColorCache",
    "CancelPlotSelection",
    "Col",
    "ColormapButton",
    "ColormapEnum",
    "ColormapIcon",
    "ColormapScale",
    "ColormapScaleFlags",
    "ColormapSlider",
    "Cond",
    "Context",
    "CreateContext",
    "DestroyContext",
    "DigitalFlags",
    "DragLineX",
    "DragLineY",
    "DragPoint",
    "DragRect",
    "DragToolFlags",
    "DummyFlags",
    "EndAlignedPlots",
    "EndDragDropSource",
    "EndDragDropTarget",
    "EndLegendPopup",
    "EndPlot",
    "EndSubplots",
    "ErrorBarsFlags",
    "GetColormapColor",
    "GetColormapCount",
    "GetColormapIndex",
    "GetColormapName",
    "GetColormapSize",
    "GetCurrentContext",
    "GetInputMap",
    "GetLastItemColor",
    "GetMarkerName",
    "GetPlotDrawList",
    "GetPlotLimits",
    "GetPlotMousePos",
    "GetPlotPos",
    "GetPlotSelection",
    "GetPlotSize",
    "GetStyle",
    "GetStyleColorName",
    "HeatmapFlags",
    "HideNextItem",
    "HistogramFlags",
    "ImageFlags",
    "InfLinesFlags",
    "InputMap",
    "IsAxisHovered",
    "IsLegendEntryHovered",
    "IsPlotHovered",
    "IsPlotSelected",
    "IsSubplotsHovered",
    "ItemFlags",
    "ItemIcon",
    "LegendFlags",
    "LineFlags",
    "Location",
    "MapInputDefault",
    "MapInputReverse",
    "Marker",
    "MouseTextFlags",
    "NextColormapColor",
    "PieChartFlags",
    "PixelsToPlot",
    "PlotBarGroups",
    "PlotBars",
    "PlotDigital",
    "PlotDummy",
    "PlotErrorBars",
    "PlotFlags",
    "PlotHeatmap",
    "PlotHistogram",
    "PlotHistogram2D",
    "PlotImage",
    "PlotInfLines",
    "PlotLine",
    "PlotPieChart",
    "PlotScatter",
    "PlotShaded",
    "PlotStairs",
    "PlotStems",
    "PlotStyle",
    "PlotText",
    "PlotToPixels",
    "Point",
    "PopColormap",
    "PopPlotClipRect",
    "PopStyleColor",
    "PopStyleVar",
    "PushColormap",
    "PushPlotClipRect",
    "PushStyleColor",
    "PushStyleVar",
    "Range",
    "Rect",
    "SampleColormap",
    "Scale",
    "ScatterFlags",
    "SetAxes",
    "SetAxis",
    "SetCurrentContext",
    "SetNextAxesLimits",
    "SetNextAxesToFit",
    "SetNextAxisLimits",
    "SetNextAxisLinks",
    "SetNextAxisToFit",
    "SetNextErrorBarStyle",
    "SetNextFillStyle",
    "SetNextLineStyle",
    "SetNextMarkerStyle",
    "SetupAxes",
    "SetupAxesLimits",
    "SetupAxis",
    "SetupAxisFormat",
    "SetupAxisLimits",
    "SetupAxisLimitsConstraints",
    "SetupAxisLinks",
    "SetupAxisScale",
    "SetupAxisTicks",
    "SetupAxisZoomConstraints",
    "SetupFinish",
    "SetupLegend",
    "SetupMouseText",
    "ShadedFlags",
    "ShowColormapSelector",
    "ShowDemoWindow",
    "ShowInputMapSelector",
    "ShowMetricsWindow",
    "ShowStyleEditor",
    "ShowStyleSelector",
    "ShowUserGuide",
    "StairsFlags",
    "StemsFlags",
    "StyleColorsAuto",
    "StyleColorsClassic",
    "StyleColorsDark",
    "StyleColorsLight",
    "StyleVar",
    "SubplotFlags",
    "TagX",
    "TagY",
    "TextFlags"
]


class Axis():
    X1 = 0
    X2 = 1
    X3 = 2
    Y1 = 3
    Y2 = 4
    Y3 = 5
    pass
class AxisFlags():
    AutoFit = 2048
    AuxDefault = 258
    Foreground = 512
    Invert = 1024
    Lock = 49152
    LockMax = 32768
    LockMin = 16384
    NoDecorations = 15
    NoGridLines = 2
    NoHighlight = 128
    NoInitialFit = 16
    NoLabel = 1
    NoMenus = 32
    NoSideSwitch = 64
    NoTickLabels = 8
    NoTickMarks = 4
    None_ = 0
    Opposite = 256
    PanStretch = 8192
    RangeFit = 4096
    pass
class BarGroupsFlags():
    Horizontal = 1024
    None_ = 0
    Stacked = 2048
    pass
class BarsFlags():
    Horizontal = 1024
    None_ = 0
    pass
class Bin():
    Rice = -3
    Scott = -4
    Sqrt = -1
    Sturges = -2
    pass
class Col():
    AxisBg = 16
    AxisBgActive = 18
    AxisBgHovered = 17
    AxisGrid = 14
    AxisText = 13
    AxisTick = 15
    Crosshairs = 20
    ErrorBar = 4
    Fill = 1
    FrameBg = 5
    InlayText = 12
    LegendBg = 8
    LegendBorder = 9
    LegendText = 10
    Line = 0
    MarkerFill = 3
    MarkerOutline = 2
    PlotBg = 6
    PlotBorder = 7
    Selection = 19
    TitleText = 11
    pass
class ColormapEnum():
    BrBG = 12
    Cool = 7
    Dark = 1
    Deep = 0
    Greys = 15
    Hot = 6
    Jet = 9
    Paired = 3
    Pastel = 2
    PiYG = 13
    Pink = 8
    Plasma = 5
    RdBu = 11
    Spectral = 14
    Twilight = 10
    Viridis = 4
    pass
class ColormapScaleFlags():
    Invert = 4
    NoLabel = 1
    None_ = 0
    Opposite = 2
    pass
class Cond():
    Always = 1
    None_ = 0
    Once = 2
    pass
class Context():
    pass
class DigitalFlags():
    None_ = 0
    pass
class DragToolFlags():
    Delayed = 8
    NoCursors = 1
    NoFit = 2
    NoInputs = 4
    None_ = 0
    pass
class DummyFlags():
    None_ = 0
    pass
class ErrorBarsFlags():
    Horizontal = 1024
    None_ = 0
    pass
class HeatmapFlags():
    ColMajor = 1024
    None_ = 0
    pass
class HistogramFlags():
    ColMajor = 16384
    Cumulative = 2048
    Density = 4096
    Horizontal = 1024
    NoOutliers = 8192
    None_ = 0
    pass
class ImageFlags():
    None_ = 0
    pass
class InfLinesFlags():
    Horizontal = 1024
    None_ = 0
    pass
class InputMap():
    def __init__(self) -> None: ...
    @property
    def Fit(self) -> int:
        """
        :type: int
        """
    @Fit.setter
    def Fit(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def Menu(self) -> int:
        """
        :type: int
        """
    @Menu.setter
    def Menu(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def OverrideMod(self) -> int:
        """
        :type: int
        """
    @OverrideMod.setter
    def OverrideMod(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def Pan(self) -> int:
        """
        :type: int
        """
    @Pan.setter
    def Pan(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def PanMod(self) -> int:
        """
        :type: int
        """
    @PanMod.setter
    def PanMod(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def Select(self) -> int:
        """
        :type: int
        """
    @Select.setter
    def Select(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def SelectCancel(self) -> int:
        """
        :type: int
        """
    @SelectCancel.setter
    def SelectCancel(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def SelectHorzMod(self) -> int:
        """
        :type: int
        """
    @SelectHorzMod.setter
    def SelectHorzMod(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def SelectMod(self) -> int:
        """
        :type: int
        """
    @SelectMod.setter
    def SelectMod(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def SelectVertMod(self) -> int:
        """
        :type: int
        """
    @SelectVertMod.setter
    def SelectVertMod(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def ZoomMod(self) -> int:
        """
        :type: int
        """
    @ZoomMod.setter
    def ZoomMod(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def ZoomRate(self) -> float:
        """
        :type: float
        """
    @ZoomRate.setter
    def ZoomRate(self, arg0: typing.SupportsFloat) -> None:
        pass
    pass
class ItemFlags():
    NoFit = 2
    NoLegend = 1
    None_ = 0
    pass
class LegendFlags():
    Horizontal = 32
    NoButtons = 1
    NoHighlightAxis = 4
    NoHighlightItem = 2
    NoMenus = 8
    None_ = 0
    Outside = 16
    Sort = 64
    pass
class LineFlags():
    Loop = 2048
    NoClip = 8192
    None_ = 0
    Segments = 1024
    Shaded = 16384
    SkipNaN = 4096
    pass
class Location():
    Center = 0
    East = 8
    North = 1
    NorthEast = 9
    NorthWest = 5
    South = 2
    SouthEast = 10
    SouthWest = 6
    West = 4
    pass
class Marker():
    Asterisk = 9
    Circle = 0
    Cross = 7
    Diamond = 2
    Down = 4
    Left = 5
    None_ = -1
    Plus = 8
    Right = 6
    Square = 1
    Up = 3
    pass
class MouseTextFlags():
    NoAuxAxes = 1
    NoFormat = 2
    None_ = 0
    ShowAlways = 4
    pass
class PieChartFlags():
    Exploding = 4096
    IgnoreHidden = 2048
    None_ = 0
    Normalize = 1024
    pass
class PlotFlags():
    CanvasOnly = 55
    Crosshairs = 256
    Equal = 128
    NoBoxSelect = 32
    NoFrame = 64
    NoInputs = 8
    NoLegend = 2
    NoMenus = 16
    NoMouseText = 4
    NoTitle = 1
    None_ = 0
    pass
class PlotStyle():
    def __init__(self) -> None: ...
    @property
    def AnnotationPadding(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @AnnotationPadding.setter
    def AnnotationPadding(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def Colormap(self) -> int:
        """
        :type: int
        """
    @Colormap.setter
    def Colormap(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def Colors(self) -> ListWrapper<ImVec4>:
        """
        :type: ListWrapper<ImVec4>
        """
    @property
    def DigitalBitGap(self) -> float:
        """
        :type: float
        """
    @DigitalBitGap.setter
    def DigitalBitGap(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def DigitalBitHeight(self) -> float:
        """
        :type: float
        """
    @DigitalBitHeight.setter
    def DigitalBitHeight(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def ErrorBarSize(self) -> float:
        """
        :type: float
        """
    @ErrorBarSize.setter
    def ErrorBarSize(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def ErrorBarWeight(self) -> float:
        """
        :type: float
        """
    @ErrorBarWeight.setter
    def ErrorBarWeight(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def FillAlpha(self) -> float:
        """
        :type: float
        """
    @FillAlpha.setter
    def FillAlpha(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def FitPadding(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @FitPadding.setter
    def FitPadding(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def LabelPadding(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @LabelPadding.setter
    def LabelPadding(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def LegendInnerPadding(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @LegendInnerPadding.setter
    def LegendInnerPadding(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def LegendPadding(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @LegendPadding.setter
    def LegendPadding(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def LegendSpacing(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @LegendSpacing.setter
    def LegendSpacing(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def LineWeight(self) -> float:
        """
        :type: float
        """
    @LineWeight.setter
    def LineWeight(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def MajorGridSize(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @MajorGridSize.setter
    def MajorGridSize(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def MajorTickLen(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @MajorTickLen.setter
    def MajorTickLen(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def MajorTickSize(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @MajorTickSize.setter
    def MajorTickSize(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def Marker(self) -> int:
        """
        :type: int
        """
    @Marker.setter
    def Marker(self, arg0: typing.SupportsInt) -> None:
        pass
    @property
    def MarkerSize(self) -> float:
        """
        :type: float
        """
    @MarkerSize.setter
    def MarkerSize(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def MarkerWeight(self) -> float:
        """
        :type: float
        """
    @MarkerWeight.setter
    def MarkerWeight(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def MinorAlpha(self) -> float:
        """
        :type: float
        """
    @MinorAlpha.setter
    def MinorAlpha(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def MinorGridSize(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @MinorGridSize.setter
    def MinorGridSize(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def MinorTickLen(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @MinorTickLen.setter
    def MinorTickLen(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def MinorTickSize(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @MinorTickSize.setter
    def MinorTickSize(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def MousePosPadding(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @MousePosPadding.setter
    def MousePosPadding(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def PlotBorderSize(self) -> float:
        """
        :type: float
        """
    @PlotBorderSize.setter
    def PlotBorderSize(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def PlotDefaultSize(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @PlotDefaultSize.setter
    def PlotDefaultSize(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def PlotMinSize(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @PlotMinSize.setter
    def PlotMinSize(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def PlotPadding(self) -> imgui.Vec2:
        """
        :type: imgui.Vec2
        """
    @PlotPadding.setter
    def PlotPadding(self, arg0: imgui.Vec2) -> None:
        pass
    @property
    def Use24HourClock(self) -> bool:
        """
        :type: bool
        """
    @Use24HourClock.setter
    def Use24HourClock(self, arg0: bool) -> None:
        pass
    @property
    def UseISO8601(self) -> bool:
        """
        :type: bool
        """
    @UseISO8601.setter
    def UseISO8601(self, arg0: bool) -> None:
        pass
    @property
    def UseLocalTime(self) -> bool:
        """
        :type: bool
        """
    @UseLocalTime.setter
    def UseLocalTime(self, arg0: bool) -> None:
        pass
    pass
class Point():
    def __init__(self, x: typing.SupportsFloat = 0, y: typing.SupportsFloat = 0) -> None: ...
    @property
    def x(self) -> float:
        """
        :type: float
        """
    @x.setter
    def x(self, arg0: typing.SupportsFloat) -> None:
        pass
    @property
    def y(self) -> float:
        """
        :type: float
        """
    @y.setter
    def y(self, arg0: typing.SupportsFloat) -> None:
        pass
    pass
class Range():
    def Clamp(self, value: typing.SupportsFloat) -> float: ...
    def Contains(self, value: typing.SupportsFloat) -> bool: ...
    def Size(self) -> float: ...
    def __init__(self, min: typing.SupportsFloat = 0, max: typing.SupportsFloat = 0) -> None: ...
    pass
class Rect():
    @typing.overload
    def Clamp(self, p: Point) -> Point: ...
    @typing.overload
    def Clamp(self, x: typing.SupportsFloat, y: typing.SupportsFloat) -> Point: ...
    @typing.overload
    def Contains(self, p: Point) -> bool: ...
    @typing.overload
    def Contains(self, x: typing.SupportsFloat, y: typing.SupportsFloat) -> bool: ...
    def Max(self) -> Point: ...
    def Min(self) -> Point: ...
    def Size(self) -> Point: ...
    def __init__(self, x_min: typing.SupportsFloat = 0, x_max: typing.SupportsFloat = 0, y_min: typing.SupportsFloat = 0, y_max: typing.SupportsFloat = 0) -> None: ...
    pass
class Scale():
    Linear = 0
    Log10 = 2
    SymLog = 3
    Time = 1
    pass
class ScatterFlags():
    NoClip = 1024
    None_ = 0
    pass
class ShadedFlags():
    None_ = 0
    pass
class StairsFlags():
    None_ = 0
    PreStep = 1024
    Shaded = 2048
    pass
class StemsFlags():
    Horizontal = 1024
    None_ = 0
    pass
class StyleVar():
    AnnotationPadding = 23
    DigitalBitGap = 8
    DigitalBitHeight = 7
    ErrorBarSize = 5
    ErrorBarWeight = 6
    FillAlpha = 4
    FitPadding = 24
    LabelPadding = 18
    LegendInnerPadding = 20
    LegendPadding = 19
    LegendSpacing = 21
    LineWeight = 0
    MajorGridSize = 15
    MajorTickLen = 11
    MajorTickSize = 13
    Marker = 1
    MarkerSize = 2
    MarkerWeight = 3
    MinorAlpha = 10
    MinorGridSize = 16
    MinorTickLen = 12
    MinorTickSize = 14
    MousePosPadding = 22
    PlotBorderSize = 9
    PlotDefaultSize = 25
    PlotMinSize = 26
    PlotPadding = 17
    pass
class SubplotFlags():
    ColMajor = 1024
    LinkAllX = 256
    LinkAllY = 512
    LinkCols = 128
    LinkRows = 64
    NoAlign = 16
    NoLegend = 2
    NoMenus = 4
    NoResize = 8
    NoTitle = 1
    None_ = 0
    ShareItems = 32
    pass
class TextFlags():
    None_ = 0
    Vertical = 1024
    pass
@typing.overload
def AddColorMap(name: str, cols: typing.Annotated[numpy.typing.ArrayLike, imgui.Vec4], qual: bool = True) -> int:
    pass
@typing.overload
def AddColorMap(name: str, cols: typing.Annotated[numpy.typing.ArrayLike, numpy.uint32], qual: bool = True) -> int:
    pass
@typing.overload
def Annotation(x: typing.SupportsFloat, y: typing.SupportsFloat, col: imgui.Vec4, pix_offset: imgui.Vec2, clamp: bool, fmt: str) -> None:
    pass
@typing.overload
def Annotation(x: typing.SupportsFloat, y: typing.SupportsFloat, col: imgui.Vec4, pix_offset: imgui.Vec2, clamp: bool, round: bool = False) -> None:
    pass
def BeginAlignedPlots(group_id: str, vertical: bool = True) -> bool:
    pass
def BeginDragDropSourceAxis(axis: typing.SupportsInt, flags: typing.SupportsInt = 0) -> bool:
    pass
def BeginDragDropSourceItem(label_id: str, flags: typing.SupportsInt = 0) -> bool:
    pass
def BeginDragDropSourcePlot(flags: typing.SupportsInt = 0) -> bool:
    pass
def BeginDragDropTargetAxis(axis: typing.SupportsInt) -> bool:
    pass
def BeginDragDropTargetLegend() -> bool:
    pass
def BeginDragDropTargetPlot() -> bool:
    pass
def BeginLegendPopup(label_id: str, mouse_button: typing.SupportsInt = 1) -> bool:
    pass
def BeginPlot(title_id: str, size: imgui.Vec2 = Vec2(-1, 0), flags: typing.SupportsInt = 0) -> bool:
    pass
def BeginSubplots(title_id: str, rows: typing.SupportsInt, cols: typing.SupportsInt, size: imgui.Vec2, flags: typing.SupportsInt = 0, row_ratios: imgui.FloatList = None, col_ratios: imgui.FloatList = None) -> bool:
    pass
def BustColorCache(plot_title_id: typing.Optional[str] = None) -> None:
    pass
def CancelPlotSelection() -> None:
    pass
def ColormapButton(label: str, size: imgui.Vec2 = Vec2(0, 0), cmap: typing.SupportsInt = -1) -> bool:
    pass
def ColormapIcon(cmap: typing.SupportsInt) -> None:
    pass
def ColormapScale(label: str, scale_min: typing.SupportsFloat, scale_max: typing.SupportsFloat, size: imgui.Vec2 = Vec2(0, 0), format: str = '%g', flags: typing.SupportsInt = 0, cmap: typing.SupportsInt = -1) -> None:
    pass
def ColormapSlider(label: str, t: imgui.FloatRef, out: imgui.Vec4 = None, format: str = '', cmap: typing.SupportsInt = -1) -> bool:
    pass
def CreateContext() -> Context:
    pass
def DestroyContext(ctx: typing.Optional[Context] = None) -> None:
    pass
def DragLineX(id: typing.SupportsInt, x: typing.SupportsFloat, col: imgui.Vec4, thickness: typing.SupportsFloat = 1, flags: typing.SupportsInt = 0) -> tuple:
    pass
def DragLineY(id: typing.SupportsInt, y: typing.SupportsFloat, col: imgui.Vec4, thickness: typing.SupportsFloat = 1, flags: typing.SupportsInt = 0) -> tuple:
    pass
def DragPoint(id: typing.SupportsInt, x: typing.SupportsFloat, y: typing.SupportsFloat, col: imgui.Vec4, size: typing.SupportsFloat = 4, flags: typing.SupportsInt = 0) -> tuple:
    pass
def DragRect(id: typing.SupportsInt, x1: typing.SupportsFloat, y1: typing.SupportsFloat, x2: typing.SupportsFloat, y2: typing.SupportsFloat, col: imgui.Vec4, flags: typing.SupportsInt = 0) -> tuple:
    pass
def EndAlignedPlots() -> None:
    pass
def EndDragDropSource() -> None:
    pass
def EndDragDropTarget() -> None:
    pass
def EndLegendPopup() -> None:
    pass
def EndPlot() -> None:
    pass
def EndSubplots() -> None:
    pass
def GetColormapColor(idx: typing.SupportsInt, cmap: typing.SupportsInt = -1) -> imgui.Vec4:
    pass
def GetColormapCount() -> int:
    pass
def GetColormapIndex(name: str) -> int:
    pass
def GetColormapName(cmap: typing.SupportsInt) -> str:
    pass
def GetColormapSize(cmap: typing.SupportsInt = -1) -> int:
    pass
def GetCurrentContext() -> Context:
    pass
def GetInputMap() -> InputMap:
    pass
def GetLastItemColor() -> imgui.Vec4:
    pass
def GetMarkerName(idx: typing.SupportsInt) -> str:
    pass
def GetPlotDrawList() -> imgui.ImDrawList:
    pass
def GetPlotLimits(x_axis: typing.SupportsInt = -1, y_axis: typing.SupportsInt = -1) -> Rect:
    pass
def GetPlotMousePos(x_axis: typing.SupportsInt = -1, y_axis: typing.SupportsInt = -1) -> Point:
    pass
def GetPlotPos() -> imgui.Vec2:
    pass
def GetPlotSelection(x_axis: typing.SupportsInt = -1, y_axis: typing.SupportsInt = -1) -> Rect:
    pass
def GetPlotSize() -> imgui.Vec2:
    pass
def GetStyle() -> PlotStyle:
    pass
def GetStyleColorName(idx: typing.SupportsInt) -> str:
    pass
def HideNextItem(hidden: bool = True, cond: typing.SupportsInt = 2) -> None:
    pass
def IsAxisHovered(axis: typing.SupportsInt) -> bool:
    pass
def IsLegendEntryHovered(label_id: str) -> bool:
    pass
def IsPlotHovered() -> bool:
    pass
def IsPlotSelected() -> bool:
    pass
def IsSubplotsHovered() -> bool:
    pass
@typing.overload
def ItemIcon(col: imgui.Vec4) -> None:
    pass
@typing.overload
def ItemIcon(col: typing.SupportsInt) -> None:
    pass
def MapInputDefault(dst: typing.Optional[InputMap] = None) -> None:
    pass
def MapInputReverse(dst: typing.Optional[InputMap] = None) -> None:
    pass
def NextColormapColor() -> imgui.Vec4:
    pass
@typing.overload
def PixelsToPlot(pix: imgui.Vec2, x_axis: typing.SupportsInt = -1, y_axis: typing.SupportsInt = -1) -> Point:
    pass
@typing.overload
def PixelsToPlot(x: typing.SupportsFloat, y: typing.SupportsFloat, x_axis: typing.SupportsInt = -1, y_axis: typing.SupportsInt = -1) -> Point:
    pass
@typing.overload
def PlotBarGroups(labels: imgui.StrList, values: imgui.DoubleList, item_count: typing.SupportsInt, group_count: typing.SupportsInt, group_size: typing.SupportsFloat = 0.67, shift: typing.SupportsFloat = 0.0, flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotBarGroups(labels: imgui.StrList, values: imgui.IntList, item_count: typing.SupportsInt, group_count: typing.SupportsInt, group_size: typing.SupportsFloat = 0.67, shift: typing.SupportsFloat = 0.0, flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotBarGroups(labels: typing.Annotated[numpy.typing.ArrayLike, str], values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], item_count: typing.SupportsInt, group_count: typing.SupportsInt, group_size: typing.SupportsFloat = 0.67, shift: typing.SupportsFloat = 0.0, flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotBars(label_id: str, values: imgui.DoubleList, bar_size: typing.SupportsFloat = 0.67, shift: typing.SupportsFloat = 0.0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotBars(label_id: str, values: imgui.IntList, bar_size: typing.SupportsFloat = 0.67, shift: typing.SupportsFloat = 0.0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotBars(label_id: str, values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], bar_size: typing.SupportsFloat = 0.67, shift: typing.SupportsFloat = 0.0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotBars(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, bar_size: typing.SupportsFloat = 0.67, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotBars(label_id: str, xs: imgui.IntList, ys: imgui.IntList, bar_size: typing.SupportsFloat = 0.67, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotBars(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], bar_size: typing.SupportsFloat = 0.67, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotDigital(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotDigital(label_id: str, xs: imgui.IntList, ys: imgui.IntList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotDigital(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
def PlotDummy(label_id: str, flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotErrorBars(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, err: imgui.DoubleList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotErrorBars(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, neg: imgui.DoubleList, pos: imgui.DoubleList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotErrorBars(label_id: str, xs: imgui.IntList, ys: imgui.IntList, err: imgui.IntList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotErrorBars(label_id: str, xs: imgui.IntList, ys: imgui.IntList, neg: imgui.IntList, pos: imgui.IntList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotErrorBars(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], err: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotErrorBars(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], neg: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], pos: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotHeatmap(label_id: str, values: imgui.DoubleList, rows: typing.SupportsInt, cols: typing.SupportsInt, scale_min: typing.SupportsFloat = 0, scale_max: typing.SupportsFloat = 0, label_fmt: str = '%.1f', bounds_min: Point = Point(0, 0), bounds_max: Point = Point(1, 1), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotHeatmap(label_id: str, values: imgui.IntList, rows: typing.SupportsInt, cols: typing.SupportsInt, scale_min: typing.SupportsFloat = 0, scale_max: typing.SupportsFloat = 0, label_fmt: str = '%.1f', bounds_min: Point = Point(0, 0), bounds_max: Point = Point(1, 1), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotHeatmap(label_id: str, values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], rows: typing.SupportsInt, cols: typing.SupportsInt, scale_min: typing.SupportsFloat = 0, scale_max: typing.SupportsFloat = 0, label_fmt: str = '%.1f', bounds_min: Point = Point(0, 0), bounds_max: Point = Point(1, 1), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotHistogram(label_id: str, values: imgui.DoubleList, bins: typing.SupportsInt = -2, bar_scale: typing.SupportsFloat = 1.0, range: Range = Range(0, 0), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotHistogram(label_id: str, values: imgui.IntList, bins: typing.SupportsInt = -2, bar_scale: typing.SupportsFloat = 1.0, range: Range = Range(0, 0), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotHistogram(label_id: str, values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], bins: typing.SupportsInt = -2, bar_scale: typing.SupportsFloat = 1.0, range: Range = Range(0, 0), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotHistogram2D(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, x_bins: typing.SupportsInt = -2, y_bins: typing.SupportsInt = -2, range: Rect = Rect(0, 0), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotHistogram2D(label_id: str, xs: imgui.IntList, ys: imgui.IntList, x_bins: typing.SupportsInt = -2, y_bins: typing.SupportsInt = -2, range: Rect = Rect(0, 0), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotHistogram2D(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], x_bins: typing.SupportsInt = -2, y_bins: typing.SupportsInt = -2, range: Rect = Rect(0, 0), flags: typing.SupportsInt = 0) -> None:
    pass
def PlotImage(label_id: str, texture: imgui.Texture, bounds_min: Point, bounds_max: Point, uv0: imgui.Vec2 = Vec2(0, 0), uv1: imgui.Vec2 = Vec2(0, 0), tint_col: imgui.Vec4 = Vec4(1, 1, 1, 1), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotInfLines(label_id: str, values: imgui.DoubleList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotInfLines(label_id: str, values: imgui.IntList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotInfLines(label_id: str, values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotLine(label_id: str, values: imgui.DoubleList, xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotLine(label_id: str, values: imgui.IntList, xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotLine(label_id: str, values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotLine(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotLine(label_id: str, xs: imgui.IntList, ys: imgui.IntList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotLine(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotPieChart(label_ids: imgui.StrList, values: imgui.DoubleList, x: typing.SupportsFloat, y: typing.SupportsFloat, radius: typing.SupportsFloat, label_fmt: str = '%.1f', angle0: typing.SupportsFloat = 90, flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotPieChart(label_ids: imgui.StrList, values: imgui.IntList, x: typing.SupportsFloat, y: typing.SupportsFloat, radius: typing.SupportsFloat, label_fmt: str = '%.1f', angle0: typing.SupportsFloat = 90, flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotPieChart(label_ids: typing.Annotated[numpy.typing.ArrayLike, str], values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], x: typing.SupportsFloat, y: typing.SupportsFloat, radius: typing.SupportsFloat, label_fmt: str = '%.1f', angle0: typing.SupportsFloat = 90, flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotScatter(label_id: str, values: imgui.DoubleList, xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotScatter(label_id: str, values: imgui.IntList, xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotScatter(label_id: str, values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotScatter(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotScatter(label_id: str, xs: imgui.IntList, ys: imgui.IntList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotScatter(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotShaded(label_id: str, values: imgui.DoubleList, yref: typing.SupportsFloat = 0, xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotShaded(label_id: str, values: imgui.IntList, yref: typing.SupportsFloat = 0, xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotShaded(label_id: str, values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], yref: typing.SupportsFloat = 0, xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotShaded(label_id: str, xs: imgui.DoubleList, ys1: imgui.DoubleList, ys2: imgui.DoubleList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotShaded(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, yref: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotShaded(label_id: str, xs: imgui.IntList, ys1: imgui.IntList, ys2: imgui.IntList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotShaded(label_id: str, xs: imgui.IntList, ys: imgui.IntList, yref: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotShaded(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys1: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys2: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotShaded(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], yref: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStairs(label_id: str, values: imgui.DoubleList, xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStairs(label_id: str, values: imgui.IntList, xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStairs(label_id: str, values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], xscale: typing.SupportsFloat = 1, xstart: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStairs(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStairs(label_id: str, xs: imgui.IntList, ys: imgui.IntList, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStairs(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStems(label_id: str, values: imgui.DoubleList, ref: typing.SupportsInt = 0, scale: typing.SupportsFloat = 1, start: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStems(label_id: str, values: imgui.IntList, ref: typing.SupportsInt = 0, scale: typing.SupportsFloat = 1, start: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStems(label_id: str, values: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ref: typing.SupportsInt = 0, scale: typing.SupportsFloat = 1, start: typing.SupportsFloat = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStems(label_id: str, xs: imgui.DoubleList, ys: imgui.DoubleList, ref: typing.SupportsInt = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStems(label_id: str, xs: imgui.IntList, ys: imgui.IntList, ref: typing.SupportsInt = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotStems(label_id: str, xs: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ys: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], ref: typing.SupportsInt = 0, flags: typing.SupportsInt = 0, offset: typing.SupportsInt = 0) -> None:
    pass
def PlotText(text: str, x: typing.SupportsFloat, y: typing.SupportsFloat, pix_offset: imgui.Vec2 = Vec2(0, 0), flags: typing.SupportsInt = 0) -> None:
    pass
@typing.overload
def PlotToPixels(plt: Point, x_axis: typing.SupportsInt = -1, y_axis: typing.SupportsInt = -1) -> imgui.Vec2:
    pass
@typing.overload
def PlotToPixels(x: typing.SupportsFloat, y: typing.SupportsFloat, x_axis: typing.SupportsInt = -1, y_axis: typing.SupportsInt = -1) -> imgui.Vec2:
    pass
def PopColormap(count: typing.SupportsInt = 1) -> None:
    pass
def PopPlotClipRect() -> None:
    pass
def PopStyleColor(count: typing.SupportsInt = 1) -> None:
    pass
def PopStyleVar(count: typing.SupportsInt = 1) -> None:
    pass
@typing.overload
def PushColormap(cmap: typing.SupportsInt) -> None:
    pass
@typing.overload
def PushColormap(name: str) -> None:
    pass
def PushPlotClipRect(expand: typing.SupportsFloat = 0) -> None:
    pass
@typing.overload
def PushStyleColor(idx: typing.SupportsInt, col: imgui.Vec4) -> None:
    pass
@typing.overload
def PushStyleColor(idx: typing.SupportsInt, col: typing.SupportsInt) -> None:
    pass
@typing.overload
def PushStyleVar(idx: typing.SupportsInt, val: float) -> None:
    pass
@typing.overload
def PushStyleVar(idx: typing.SupportsInt, val: imgui.Vec2) -> None:
    pass
@typing.overload
def PushStyleVar(idx: typing.SupportsInt, val: int) -> None:
    pass
def SampleColormap(t: typing.SupportsFloat, cmap: typing.SupportsInt = -1) -> imgui.Vec4:
    pass
def SetAxes(x_axis: typing.SupportsInt, y_axis: typing.SupportsInt) -> None:
    pass
def SetAxis(axis: typing.SupportsInt) -> None:
    pass
def SetCurrentContext(ctx: Context) -> None:
    pass
def SetNextAxesLimits(x_min: typing.SupportsFloat, x_max: typing.SupportsFloat, y_min: typing.SupportsFloat, y_max: typing.SupportsFloat, cond: typing.SupportsInt = 2) -> None:
    pass
def SetNextAxesToFit() -> None:
    pass
def SetNextAxisLimits(axis: typing.SupportsInt, v_min: typing.SupportsFloat, v_max: typing.SupportsFloat, cond: typing.SupportsInt = 2) -> None:
    pass
def SetNextAxisLinks(arg0: typing.SupportsInt, arg1: imgui.DoubleRef, arg2: imgui.DoubleRef) -> None:
    pass
def SetNextAxisToFit(axis: typing.SupportsInt) -> None:
    pass
def SetNextErrorBarStyle(col: imgui.Vec4 = IMPLOT_AUTO_COL, size: typing.SupportsFloat = -1, weight: typing.SupportsFloat = -1) -> None:
    pass
def SetNextFillStyle(col: imgui.Vec4 = IMPLOT_AUTO_COL, alpha_mod: typing.SupportsFloat = -1) -> None:
    pass
def SetNextLineStyle(col: imgui.Vec4 = IMPLOT_AUTO_COL, weight: typing.SupportsFloat = -1) -> None:
    pass
def SetNextMarkerStyle(marker: typing.SupportsInt = -1, size: typing.SupportsFloat = -1, fill: imgui.Vec4 = IMPLOT_AUTO_COL, weight: typing.SupportsFloat = -1, outline: imgui.Vec4 = IMPLOT_AUTO_COL) -> None:
    pass
def SetupAxes(x_label: str, y_label: str, x_flags: typing.SupportsInt = 0, y_flags: typing.SupportsInt = 0) -> None:
    pass
def SetupAxesLimits(x_min: typing.SupportsFloat, x_max: typing.SupportsFloat, y_min: typing.SupportsFloat, y_max: typing.SupportsFloat, cond: typing.SupportsInt = 2) -> None:
    pass
def SetupAxis(axis: typing.SupportsInt, label: typing.Optional[str] = None, flags: typing.SupportsInt = 0) -> None:
    pass
def SetupAxisFormat(axis: typing.SupportsInt, format: str) -> None:
    pass
def SetupAxisLimits(axis: typing.SupportsInt, v_min: typing.SupportsFloat, v_max: typing.SupportsFloat, cond: typing.SupportsInt = 2) -> None:
    pass
def SetupAxisLimitsConstraints(axis: typing.SupportsInt, v_min: typing.SupportsFloat, v_max: typing.SupportsFloat) -> None:
    pass
def SetupAxisLinks(axis: typing.SupportsInt, link_min: imgui.DoubleRef, link_max: imgui.DoubleRef) -> None:
    pass
def SetupAxisScale(axis: typing.SupportsInt, scale: typing.SupportsInt) -> None:
    pass
@typing.overload
def SetupAxisTicks(axis: typing.SupportsInt, v_min: typing.SupportsFloat, v_max: typing.SupportsFloat, n_ticks: typing.SupportsInt, labels: imgui.StrList = None, keep_default: bool = False) -> None:
    pass
@typing.overload
def SetupAxisTicks(axis: typing.SupportsInt, values: imgui.DoubleList, labels: imgui.StrList = None, keep_default: bool = False) -> None:
    pass
def SetupAxisZoomConstraints(axis: typing.SupportsInt, z_min: typing.SupportsFloat, z_max: typing.SupportsFloat) -> None:
    pass
def SetupFinish() -> None:
    pass
def SetupLegend(location: typing.SupportsInt, flags: typing.SupportsInt = 0) -> None:
    pass
def SetupMouseText(location: typing.SupportsInt, flags: typing.SupportsInt = 0) -> None:
    pass
def ShowColormapSelector(label: str) -> bool:
    pass
def ShowDemoWindow(p_open: imgui.BoolRef = None) -> None:
    pass
def ShowInputMapSelector(label: str) -> bool:
    pass
def ShowMetricsWindow(p_open: imgui.BoolRef = None) -> None:
    pass
def ShowStyleEditor(ref: typing.Optional[PlotStyle] = None) -> None:
    pass
def ShowStyleSelector(label: str) -> bool:
    pass
def ShowUserGuide() -> None:
    pass
def StyleColorsAuto(dst: typing.Optional[PlotStyle] = None) -> None:
    pass
def StyleColorsClassic(dst: typing.Optional[PlotStyle] = None) -> None:
    pass
def StyleColorsDark(dst: typing.Optional[PlotStyle] = None) -> None:
    pass
def StyleColorsLight(dst: typing.Optional[PlotStyle] = None) -> None:
    pass
@typing.overload
def TagX(x: typing.SupportsFloat, col: imgui.Vec4, fmt: str) -> None:
    pass
@typing.overload
def TagX(x: typing.SupportsFloat, col: imgui.Vec4, round: bool = False) -> None:
    pass
@typing.overload
def TagY(y: typing.SupportsFloat, col: imgui.Vec4, fmt: str) -> None:
    pass
@typing.overload
def TagY(y: typing.SupportsFloat, col: imgui.Vec4, round: bool = False) -> None:
    pass
