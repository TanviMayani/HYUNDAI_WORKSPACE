import * as XLSX from "xlsx";
export const exportToXls = (data, name = "exported_data") => {
  const worksheet = XLSX.utils.json_to_sheet(data);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");
  XLSX.writeFile(workbook, `${name}.xlsx`);
};

export const tableToExcel = (data) => {
  const tableData = [data.heading, ...data.rows];
  const worksheet = XLSX.utils.aoa_to_sheet(tableData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");
  XLSX.writeFile(workbook, "exported_table.xlsx");
};
