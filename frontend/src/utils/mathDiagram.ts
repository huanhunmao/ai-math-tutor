export interface DiagramData {
  type: "circle" | "sector" | "rectangle" | "square" | "trapezoid" | "triangle" | "coordinate";
  title: string;
  labels: string[];
}

function findNumber(question: string, pattern: RegExp) {
  const match = question.match(pattern);
  return match?.[1] ?? null;
}

export function getDiagramData(question: string): DiagramData | null {
  const text = question.replace(/\s+/g, "");

  if (/扇形/.test(text)) {
    const radius =
      findNumber(text, /半径(?:是|为)?(\d+(?:\.\d+)?)/) ||
      findNumber(text, /r=(\d+(?:\.\d+)?)/i);
    const angle =
      findNumber(text, /圆心角(?:是|为)?(\d+(?:\.\d+)?)/) ||
      findNumber(text, /角(?:度)?(?:是|为)?(\d+(?:\.\d+)?)/);

    return {
      type: "sector",
      title: "扇形示意图",
      labels: [
        radius ? `半径 ${radius}` : "半径 r",
        angle ? `圆心角 ${angle}°` : "圆心角 θ",
      ],
    };
  }

  if (/圆|直径|半径/.test(text)) {
    const radius =
      findNumber(text, /半径(?:是|为)?(\d+(?:\.\d+)?)/) ||
      findNumber(text, /r=(\d+(?:\.\d+)?)/i);
    const diameter =
      findNumber(text, /直径(?:是|为)?(\d+(?:\.\d+)?)/) ||
      (radius ? String(Number(radius) * 2) : null);

    return {
      type: "circle",
      title: "圆形示意图",
      labels: [
        radius ? `半径 ${radius}` : "半径 r",
        diameter ? `直径 ${diameter}` : "直径 d",
      ],
    };
  }

  if (/正方形/.test(text)) {
    const side = findNumber(text, /边长(?:是|为)?(\d+(?:\.\d+)?)/);

    return {
      type: "square",
      title: "正方形示意图",
      labels: [side ? `边长 ${side}` : "边长 a"],
    };
  }

  if (/长方形|矩形/.test(text)) {
    const length = findNumber(text, /长(?:是|为)?(\d+(?:\.\d+)?)/);
    const width = findNumber(text, /宽(?:是|为)?(\d+(?:\.\d+)?)/);

    return {
      type: "rectangle",
      title: "矩形示意图",
      labels: [
        length ? `长 ${length}` : "长 a",
        width ? `宽 ${width}` : "宽 b",
      ],
    };
  }

  if (/梯形/.test(text)) {
    const topBase = findNumber(text, /上底(?:是|为)?(\d+(?:\.\d+)?)/);
    const bottomBase = findNumber(text, /下底(?:是|为)?(\d+(?:\.\d+)?)/);
    const height = findNumber(text, /高(?:是|为)?(\d+(?:\.\d+)?)/);

    return {
      type: "trapezoid",
      title: "梯形示意图",
      labels: [
        topBase ? `上底 ${topBase}` : "上底 a",
        bottomBase ? `下底 ${bottomBase}` : "下底 b",
        height ? `高 ${height}` : "高 h",
      ],
    };
  }

  if (/三角形|直角三角形|等腰三角形/.test(text)) {
    const sideA = findNumber(text, /边长(?:是|为)?(\d+(?:\.\d+)?)/);
    const sideB = findNumber(text, /底(?:边)?(?:是|为)?(\d+(?:\.\d+)?)/);

    return {
      type: "triangle",
      title: "三角形示意图",
      labels: [
        sideA ? `边 ${sideA}` : "边 a",
        sideB ? `底 ${sideB}` : "底 b",
      ],
    };
  }

  if (/坐标系|坐标平面|点A|点B|x轴|y轴|原点/.test(text)) {
    const pointA = text.match(/点A[（(]([^，。,；;)）]+)[)）]/)?.[1] ?? null;
    const pointB = text.match(/点B[（(]([^，。,；;)）]+)[)）]/)?.[1] ?? null;

    return {
      type: "coordinate",
      title: "坐标系示意图",
      labels: [
        pointA ? `A(${pointA})` : "A(x1, y1)",
        pointB ? `B(${pointB})` : "B(x2, y2)",
      ],
    };
  }

  return null;
}
