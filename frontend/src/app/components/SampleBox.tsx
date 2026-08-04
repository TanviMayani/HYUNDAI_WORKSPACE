import Popup from "./Popup/Popup";
import { Box, Button, Grid, Typography } from "@mui/material";
import DocViewer from "./DocViewer";
import { useParams } from "react-router-dom";
import { useGetSampleQuery } from "../redux/features/commonApis";
import { saveAs } from "file-saver";
import { useEffect } from "react";
import { useListMethodQuery } from "../redux/features/jobs";
import { useState } from "react";

const SampleBox = ({ open, onClose, isDoc = "" }) => {
  const [methodId, setMethodId] = useState("");
  const [skip, setSkip] = useState(true);

  const { id: sampleId } = useParams();

  const { data: samples } = useGetSampleQuery(
    {
      id: sampleId,
      method_id: isDoc ? methodId : "",
    },
    { skip }
  );
  const { data: methodData, refetch: methodFetch } = useListMethodQuery({});

  const downloadPDF = async (item) => {
    const response = await fetch(item);
    const blob = await response.blob();
    saveAs(blob, `${item?.slice(-10)}`);
  };

  useEffect(() => {
    methodFetch();
  }, [isDoc]);

  useEffect(() => {
    if ((isDoc && methodId) || open) setSkip(false);
  }, [isDoc, methodId, open]);

  useEffect(() => {
    setMethodId(methodData?.length > 0 && methodData[0]?.id);
  }, [methodData]);

  return (
    <Popup open={open} onClose={onClose}>
      {isDoc && (
        <Box
          display={"flex"}
          flexWrap={"wrap"}
          gap={2}
          mb={5}
          justifyContent={"center"}
        >
          {methodData?.length > 0 &&
            methodData?.map((item) => {
              return (
                <Typography
                  border={"1px solid #444"}
                  sx={{ cursor: "pointer" }}
                  variant="body1"
                  px={3}
                  className={item.id === methodId ? "secondary-pink" : ""}
                  onClick={() => {
                    setMethodId(item.id);
                  }}
                >
                  {item.display_name?.replace("Extraction", " ")}
                </Typography>
              );
            })}
        </Box>
      )}
      <Grid container width={"100%"} spacing={2}>
        {!samples && (
          <Box
            display={"flex"}
            alignItems={"center"}
            justifyContent={"center"}
            width={"100%"}
            height={"30vh"}
          >
            <Typography variant="h6" className="secondary-pink">
              No sample found!
            </Typography>
          </Box>
        )}
        {samples?.length > 0 &&
          samples.map((item, index) => {
            const isPdf = item?.includes(".pdf");
            return (
              <Grid item xs={3} key={index}>
                {isPdf ? (
                  <DocViewer url={item} width="100%" height="250px" />
                ) : (
                  <img src={item} style={{ width: "100%" }} alt="" />
                )}

                <Button
                  variant="outlined"
                  size="small"
                  sx={{ px: 1, py: 0.1, mt: 1 }}
                  fullWidth
                  onClick={() => downloadPDF(item)}
                >
                  Download
                </Button>
              </Grid>
            );
          })}
      </Grid>
    </Popup>
  );
};

export default SampleBox;
