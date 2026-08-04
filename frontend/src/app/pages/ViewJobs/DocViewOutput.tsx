import { CropFree } from "@mui/icons-material";
import { Box, Grid, Paper, Typography } from "@mui/material";
import "@react-pdf-viewer/zoom/lib/styles/index.css";
import "@react-pdf-viewer/core/lib/styles/index.css";
import { useEffect, useState } from "react";
import CenterIcon from "../../components/CenterIcon";
import { useGetDocumentQuery } from "../../redux/features/jobs";
import { NoOutput } from "./OutputViewer";
import ArrowLeftIcon from "@mui/icons-material/ArrowLeft";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import { truncate } from "../../utils/functions.js";
import FullPopup from "../../components/Popup/FullPopup.js";
import DownloadIcon from "@mui/icons-material/Download";
import { downloadPDF } from "../../utils/commons/download.js";
import DocLoader from "../../components/DocLoader.js";
import DocViewer from "../../components/DocViewer.js";

interface DocViewOutputProps {
  id: string;
  onPage: (number) => void;
  page: number;
  isComapre: boolean;
}

interface DocumentData {
  name: string;
  document_url: string | undefined;
  document_id: string | undefined;
  type: string;
}

const DocViewOutput: React.FC<DocViewOutputProps> = ({
  id,
  onPage,
  page,
  isComapre,
}) => {
  const [skip, setSkip] = useState<boolean>(true);
  const [open, setOpen] = useState<boolean>(false);
  const { data, refetch, isFetching } = useGetDocumentQuery(id, { skip });
  const [result, setResult] = useState<DocumentData | null>(null);

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
    if (data?.length > 0) {
      const doc = data[0];
      const docUrl = doc?.document_url || doc?.file_url;
      setResult({
        ...doc,
        document_url: docUrl,
      });
    }
  }, [data, page]);

  return (
    <Grid
      item
      xs={12}
      md={12}
      lg={isComapre ? 6 : 4}
      height={"100%"}
      position={"relative"}
    >
      <Box
        display={"flex"}
        alignItems={"center"}
        justifyContent={"space-between"}
      >
        <Typography variant="h6" fontWeight={"600"} color={"primary"}>
          Preview File
        </Typography>
        {result?.document_url && (
          <Box display={"flex"} gap={2}>
            <CenterIcon>
              <DownloadIcon
                onClick={() =>
                  downloadPDF(result?.document_url, result?.document_id)
                }
              />
            </CenterIcon>
            <CenterIcon>
              <CropFree onClick={() => setOpen(true)} />
            </CenterIcon>
          </Box>
        )}
      </Box>
      {result?.document_url && (
        <Box
          className="defaultShadow defaultRadius"
          p={2}
          bgcolor={"white"}
          display={"flex"}
          justifyContent={"center"}
          mt={2}
          height={"50px"}
        >
          <Box
            display={"flex"}
            width={"100%"}
            justifyContent={"space-between"}
            alignItems={"center"}
          >
            <Typography variant="body2">
              {truncate(result?.document_name) || "PDF Viewer"}
            </Typography>
            {/* <Box
              display={"flex"}
              justifyContent={"space-between"}
              alignItems={"center"}
            >
              <Box display={"flex"} alignItems={"center"} gap={1}>
                <CenterIcon>
                  <ArrowLeftIcon onClick={() => page > 1 && onPage(page - 1)} />
                </CenterIcon>
                <Typography fontWeight={"bold"} variant="body2">
                  {page} of {data?.length}
                </Typography>
                <CenterIcon>
                  <ArrowRightIcon
                    onClick={() => page < data?.length && onPage(page + 1)}
                  />
                </CenterIcon>
              </Box>
            </Box> */}
          </Box>
        </Box>
      )}
      <Box>
        <Paper
          elevation={0}
          className="defaultShadow"
          sx={{
            background: (theme) => theme.palette.common.white,
            mt: 2,
            height: "100%",
            overflow: "auto",
          }}
        >
          <Grid container wrap="nowrap">
            <Grid item xs>
              <Paper
                elevation={0}
                sx={{
                  height: "100%",
                  background: (theme) => theme.palette.common.white,
                }}
              >
                {isFetching ? (
                  <DocLoader />
                ) : (
                  <>
                    {result?.document_url ? (
                      <>
                        {result?.type === "application/pdf" ? (
                          <DocViewer
                            url={result.document_url}
                            height="750px"
                            width="100%"
                          />
                        ) : (
                          <img
                            style={{ width: "100%", transform: "scale(1)" }}
                            src={result.document_url}
                            alt=""
                          />
                        )}
                      </>
                    ) : (
                      <NoOutput />
                    )}
                  </>
                )}
              </Paper>
            </Grid>
          </Grid>
        </Paper>
      </Box>
      <FullPopup open={open} close={() => setOpen(false)} title={result?.name}>
        <img src={result?.document_url} style={{ height: "100%" }} alt="" />
      </FullPopup>
    </Grid>
  );
};

export default DocViewOutput;
