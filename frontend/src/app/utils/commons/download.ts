import { saveAs } from "file-saver";

export const downloadPDF = async (data, name) => {
  const response = await fetch(data);
  const blob = await response.blob();
  saveAs(blob, name);
};
