"use client";

// components/TrendChart.tsx — ECharts line chart wrapper for APIx / route trends

import ReactECharts from "echarts-for-react";
import type { IndexValue } from "@/types";

interface Series {
  name:   string;
  data:   IndexValue[];
  color?: string;
}

interface Props {
  series:    Series[];
  title?:    string;
  height?:   number;
  showLegend?: boolean;
}

export default function TrendChart({
  series,
  title,
  height = 320,
  showLegend = false,
}: Props) {
  const option = {
    backgroundColor: "transparent",
    title: title
      ? {
          text:      title,
          textStyle: { fontSize: 14, fontWeight: 600, color: "inherit" },
          left:      "left",
        }
      : undefined,
    tooltip: {
      trigger:   "axis",
      backgroundColor: "rgba(30, 34, 45, 0.95)",
      borderColor: "#2a2e39",
      textStyle: { color: "#d1d4dc" },
      formatter: (params: any[]) => {
        const d = params[0].axisValue;
        return (
          `<b>${d}</b><br/>` +
          params
            .map(
              (p: any) =>
                `<span style="color:${p.color}">●</span> ${p.seriesName}: <b>${p.value[1].toFixed(2)}</b>`
            )
            .join("<br/>")
        );
      },
    },
    legend: showLegend
      ? { bottom: 0, textStyle: { color: "#b2b5be" } }
      : undefined,
    grid: { left: 50, right: 50, top: 20, bottom: showLegend ? 40 : 30 },
    xAxis: {
      type:        "time",
      axisLabel:   { color: "#b2b5be", fontSize: 11 },
      axisLine:    { lineStyle: { color: "#2a2e39" } },
      splitLine:   { show: true, lineStyle: { color: "#1f2937", type: "dashed", opacity: 0.3 } },
      axisPointer: {
        show: true,
        type: "line",
        lineStyle: { color: "#2962ff", type: "dashed", width: 1 },
        label: { show: true, backgroundColor: "#2962ff", color: "#ffffff", fontSize: 11 }
      }
    },
    yAxis: {
      type:       "value",
      scale:      true,
      position:   "right",
      axisLabel:  { color: "#b2b5be", fontSize: 11 },
      splitLine:  { show: true, lineStyle: { color: "#1f2937", type: "dashed", opacity: 0.3 } },
      axisPointer: {
        show: true,
        type: "line",
        lineStyle: { color: "#2962ff", type: "dashed", width: 1 },
        label: { show: true, backgroundColor: "#2962ff", color: "#ffffff", fontSize: 11 }
      }
    },
    series: series.map((s, i) => ({
      name:       s.name,
      type:       "line",
      smooth:     true,
      symbol:     "circle",
      symbolSize: 4,
      lineStyle:  { width: 2.5, color: s.color ?? "#2962ff" },
      itemStyle:  { color: s.color ?? "#2962ff" },
      areaStyle: series.length === 1
        ? {
            color: {
              type:       "linear",
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: (s.color ?? "#2962ff") + "40" },
                { offset: 1, color: "transparent" },
              ],
            },
          }
        : undefined,
      data: s.data.map((pt) => [pt.date, pt.index_value]),
    })),
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: height === 0 ? "100%" : height, width: "100%" }}
      opts={{ renderer: "svg" }}
      theme="dark"
    />
  );
}

const DEFAULT_COLORS = [
  "#3b82f6", "#10b981", "#f59e0b",
  "#ef4444", "#8b5cf6", "#ec4899",
];
