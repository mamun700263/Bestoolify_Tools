import API from "@/lib/api";

export async function downloadMonitorPings(
  monitorId: string,
  fileType: "csv" | "json" | "excel"
) {
  const response = await API.get(
    `/uptime/pings/download/${monitorId}`,
    {
      params: {
        file_type: fileType,
      },
      responseType: "blob",
    }
  );

  const url = window.URL.createObjectURL(response.data);

  const link = document.createElement("a");
  link.href = url;
  link.download = `results.${fileType === "excel" ? "xlsx" : fileType}`;

  link.click();

  window.URL.revokeObjectURL(url);
}