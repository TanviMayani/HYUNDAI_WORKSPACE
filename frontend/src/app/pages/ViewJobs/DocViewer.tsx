import {
  Box,
  List,
  ListItem,
  Typography,
  ListItemButton,
  ListItemText,
  Divider,
} from "@mui/material";
import dayjs from "dayjs";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import { useGetJobQuery } from "../../redux/features/jobs";
import { useEffect, useState } from "react";
import ReplyIcon from "@mui/icons-material/Reply";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import { formatBytes } from "../../utils/functions";
import CenterIcon from "../../components/CenterIcon";
import { truncate } from "../../utils/functions.js";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import DocLoader from "../../components/DocLoader.js";

interface DocType {
  id: string;
  job_start_time: string;
  status: string;
  source: any[];
  job_name: string;
}

interface DocViewerProps {
  id: string;
  onDocument: (docId: string) => void;
}

const DocViewer: React.FC<DocViewerProps> = ({ id, onDocument }) => {
  const navigate = useNavigate();
  const { data, refetch, isFetching } = useGetJobQuery(id);
  const [item, setItem] = useState<DocType | null>(null);

  useEffect(() => {
    refetch();
  }, [id, refetch]);

  useEffect(() => {
    if (data && data.length > 0) {
      setItem(data[0]);
    }
  }, [data]);

  return (
    <>
      <Box bgcolor={"white"} mb={2} borderRadius={2} className="defaultShadow">
        <Box mb={0} p={2}>
          <Box display={"flex"} alignItems={"center"} gap={2}>
            <CenterIcon>
              <ReplyIcon onClick={() => navigate(-1)} />
            </CenterIcon>

            <Box>
              <Typography
                variant="h6"
                fontSize={14}
                fontWeight={"bold"}
                sx={(theme) => ({
                  color: theme.palette.primary.main,
                })}
              >
                {item?.job_name}
              </Typography>
              <Typography variant="h6" fontSize={11}>
                {item?.id}
              </Typography>
            </Box>
          </Box>

          <Box
            display={"flex"}
            alignItems={"center"}
            justifyContent={"space-between"}
            mt={1}
          >
            <Typography color="#555" fontSize={14} fontWeight={"bold"}>
              Documents:{" "}
              <span className="secondary-pink">{item?.source.length}</span>
            </Typography>
            <Typography
              variant="caption"
              fontWeight={"600"}
              display={"flex"}
              alignItems={"center"}
              gap={1}
            >
              {dayjs(item?.job_start_time).format("DD/MM/YYYY hh:mm A")}{" "}
              <CalendarMonthIcon />
            </Typography>
          </Box>
        </Box>
        <Divider />
        <Box mt={2}>
          {isFetching ? (
            <DocLoader />
          ) : (
            <List>
              {item?.source &&
                item?.source?.length > 0 &&
                item.source.map((ele) => (
                  <ListItem
                    key={ele.document_id}
                    disablePadding
                    onClick={() =>
                      item?.status !== "Pending" && item?.status !== "In_Process"
                        ? onDocument(ele.document_id)
                        : toast.error("Status is still processing. Please wait...")
                    }
                    secondaryAction={
                      <Box
                        bgcolor={"#e3e3e3"}
                        px={1}
                        fontSize={"12px"}
                        borderRadius={1}
                      >
                        {formatBytes(ele.size)}
                      </Box>
                    }
                  >
                    <ListItemButton className="list-hover" title={ele.name}>
                      <PictureAsPdfIcon className="secondary-pink" />
                      <ListItemText
                        primaryTypographyProps={{
                          sx: { fontSize: "14px", ml: 1 },
                        }}
                        primary={truncate(ele.name, 30)}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
            </List>
          )}
        </Box>
      </Box>
    </>
  );
};

export default DocViewer;
