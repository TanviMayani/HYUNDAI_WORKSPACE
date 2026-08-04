import AddIcon from "@mui/icons-material/Add";
import { Box, Button } from "@mui/material";
import { useState } from "react";
import PLUS from "../../../assets/plus.png";
import DocDrawer from "./DocDrawer";
import QueryChat from "./QueryChat";

const CreateInstance = ({ refetch, data, id, getDocData }) => {
  const [openDrawer, setOpenDrawer] = useState<boolean>(false);

  const closeDrawer = () => {
    setOpenDrawer(false);
  };

  return (
    <>
      <Box>
        {data?.length > 0 ? (
          <QueryChat id={id} items={getDocData} />
        ) : ( 
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            mt={10}
          >
            <img src={PLUS} style={{ width: "300px" }} alt="" />
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDrawer(true)}
            >
              Create Instance
            </Button>
          </Box>
        )}
      </Box>
      <DocDrawer
        open={openDrawer}
        closeDrawer={closeDrawer}
        refetch={refetch}
        editable={false}
        data={2}
        id=""
        instanceRef={""}
      />
    </>
  );
};

export default CreateInstance;
