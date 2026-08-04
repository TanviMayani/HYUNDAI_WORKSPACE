import { Grid, Typography, Box, Tabs, Tab } from "@mui/material";
import { CropFree } from "@mui/icons-material";
import { useGetDocumentQuery } from "../../redux/features/jobs";
import { useEffect, useState } from "react";
import CenterIcon from "../../components/CenterIcon";
import Table from "./output/Table";
import Form from "./output/Form";
import ImageOutput from "./output/ImageOutput";
import Line from "./output/Line";
import NoData from "../../../assets/nodata.png";
import DownloadIcon from "@mui/icons-material/Download";

interface ResultType {
  line?: {
    text: string;
  };
  form?: string[];
  table?: string[];
  signature?: string[];
  barcode?: string;
}

interface BoxContainerProps {
  children: React.ReactNode;
  title: string;
  handleTrue: () => void;
  handleDownload: () => void;
}

export const NoOutput: React.FC<{
  text?: string;
}> = ({ text = "No Data Found!" }) => {
  return (
    <Box
      display={"flex"}
      height="400px"
      borderRadius={2}
      flexDirection={"column"}
      alignItems={"center"}
      bgcolor={"white"}
      justifyContent={"center"}
      className="secondary-pink "
      fontWeight={"bold"}
    >
      <img style={{ width: "200px" }} src={NoData} alt="" />
      {text}
    </Box>
  );
};

export const BoxContainer: React.FC<BoxContainerProps> = ({
  children,
  title,
  handleTrue,
  handleDownload,
}) => {
  return (
    <Box
      p={2}
      bgcolor={"white"}
      className="defaultShadow"
      mb={3}
      maxHeight={"70vh"}
      overflow={"auto"}
    >
      <Grid container spacing={2}>
        <Grid item xs>
          <Box
            display={"flex"}
            justifyContent={"space-between"}
            alignItems={"center"}
            mb={2}
          >
            <Typography
              variant="h6"
              fontWeight={"600"}
              className="secondary-pink"
            >
              {title}
            </Typography>
            <Box display={"flex"} gap={2}>
              <CenterIcon>
                <DownloadIcon
                  className="secondary-pink"
                  onClick={handleDownload}
                />
              </CenterIcon>
              <CenterIcon>
                <CropFree className="secondary-pink" onClick={handleTrue} />
              </CenterIcon>
            </Box>
          </Box>
          <Box height={"100%"} sx={{ wordWrap: "break-word" }}>
            {children}
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

interface OutputViewerProps {
  id: string;
  page: number;
}

const OutputViewer: React.FC<OutputViewerProps> = ({ id, page }) => {
  const [skip, setSkip] = useState(true);
  const { data, refetch } = useGetDocumentQuery(id, { skip });
  const [result, setResult] = useState<ResultType | null>(null);
  const [value, setValue] = useState(1);
  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
    // console.log(event);
  };

  useEffect(() => {
    if (id) {
      setSkip(false);
    }
  }, [id]);

  useEffect(() => {
    if (!skip) {
      refetch();
    }
  }, [skip]);

  useEffect(() => {
    if (data && data[0]) {
      let rawResult = data[0]?.result;
      if (typeof rawResult === "string") {
        try {
          rawResult = JSON.parse(rawResult);
        } catch (e) {
          console.error("Failed to parse result JSON", e);
        }
      }
      if (Array.isArray(rawResult)) {
        rawResult = rawResult.find((item: any) => item.page_number === page) || rawResult[0];
      }
      setResult(rawResult);
    }
  }, [data, page]);

  return (
    <>
      {result && (
        <Box
          sx={{ maxWidth: "100%", bgcolor: "white", px: 0 }}
          mb={3}
          display={"flex"}
          className="defaultShadow defaultRadius"
        >
          <Tabs
            value={value}
            onChange={handleChange}
            variant="scrollable"
            scrollButtons
            allowScrollButtonsMobile
          >
            {result?.line && <Tab label="Line" value={7} />}
            {result?.form && Object.keys(result.form).length > 0 && (
              <Tab label="Forms" value={1} />
            )}
            {result?.table && Object.keys(result?.table).length > 0 && (
              <Tab label="Table" value={2} />
            )}
            {/* @ts-expect-error: this is fine */}
            {result?.signature?.length > 0 && (
              <Tab label="Signature" value={3} />
            )}
            {/* @ts-expect-error: this is fine */}
            {result?.barcode?.length > 0 && <Tab label="Barcode" value={4} />}
          </Tabs>
        </Box>
      )}
      {result && value ? (
        <Box>
          {/* @ts-expect-error: this is fine */}
          {value === 7 && <Line result={result} />}
          {/* @ts-expect-error: this is fine */}
          {value === 1 && <Form result={result} />}
          {/* @ts-expect-error: this is fine */}
          {value === 2 && <Table result={result} />}
          {/* @ts-expect-error: this is fine */}
          {value === 3 && <ImageOutput result={result?.signature} />}
          {/* @ts-expect-error: this is fine */}
          {value === 4 && (
            <ImageOutput result={result?.barcode} title="Barcode" />
          )}
        </Box>
      ) : (
        <NoOutput text={result ? "Please select a option" : "No Data Found!"} />
      )}
    </>
  );
};

export default OutputViewer;
