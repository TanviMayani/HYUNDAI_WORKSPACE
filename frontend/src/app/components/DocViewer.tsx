import { Box } from "@mui/material";
import { Viewer, Worker, SpecialZoomLevel } from "@react-pdf-viewer/core";

const DocViewer = ({
  url,
  height = "90vh",
  width = "900px",
  zoomPluginInstance = false,
}) => {
  return (
    <Box width={width} mt={0}>
      <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.js">
        <div style={{ height: height, width: "100%" }}>
          <Viewer
            fileUrl={url}
            defaultScale={SpecialZoomLevel.PageWidth}
            plugins={[zoomPluginInstance]}
          />
        </div>
      </Worker>
    </Box>
  );
};

export default DocViewer;
