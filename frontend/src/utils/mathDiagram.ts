export interface DiagramData {
  type: "circle" | "rectangle" | "triangle";
  title: string;
  labels: string[];
}

function findNumber(question: string, pattern: RegExp) {
  const match = question.match(pattern);
  return match?.[1] ?? null;
}

export function getDiagramData(question: string): DiagramData | null {
  const text = question.replace(/\s+/g, "");

  if (/圆|直径|半径|扇形/.test(text)) {
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

  return null;
}
