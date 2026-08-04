import { Box, CircularProgress, Typography } from "@mui/material";

const DocLoader = () => {
  return (
    <Box
      height="100%"
      width="100%"
      display={"flex"}
      bgcolor={"white"}
      flexDirection={"column"}
      justifyContent={"center"}
      gap={2}
      py={6}
      borderRadius={2}
      alignItems={"center"}
    >
      <CircularProgress size={"30px"} />{" "}
      <Typography
        variant="body1"
        fontWeight={"bold"}
        className="secondary-pink"
      >
        Loading...
      </Typography>
    </Box>
  );
};

export default DocLoader;
