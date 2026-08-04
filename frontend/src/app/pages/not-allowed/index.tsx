import MainBox from "../../components/MainBox";
import TopPageHeader from "../../components/TopPageHeader";
import { Box, Typography } from "@mui/material";
import DENIED from "../../../assets/denied.png"

const NotAllowed = () => {
  return (
    <>
      <TopPageHeader title="Coming Soon" />
      <MainBox>
        <Box
          display={"flex"}
          alignItems={"center"}
          flexDirection={"column"}
          width={"100%"}
          height={"70vh"}
          gap={2}
          justifyContent={"center"}
        >
            <img src={DENIED} alt="" style={{width: "200px"}}/>
          <Typography variant="h5" className="secondary-pink">
            You are not allowed for this page!
          </Typography>
        </Box>
      </MainBox>
    </>
  );
};

export default NotAllowed;
