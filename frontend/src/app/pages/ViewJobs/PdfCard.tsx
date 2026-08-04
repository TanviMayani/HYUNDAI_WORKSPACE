import { Box } from "@mui/material";
import FileUploadCard from "../../components/FileUploadCard.js";

const PdfCard = ({ data, onItemChange, fileResponse, editable }) => {
  const handleDataChange = (newData) => {
    onItemChange(newData);
  };

  return (
    <>
      <Box mt={2} width={"100%"} maxHeight={"150px"} overflow={"auto"}>
        {data.length > 0 &&
          Object.values(data).map((item, index) => {
            return (
              <>
                <FileUploadCard
                  item={item}
                  key={index}
                  onDataChange={handleDataChange}
                />
              </>
            );
          })}

        {editable &&
          fileResponse?.length > 0 &&
          fileResponse?.map((ele, index) => {
            return (
              <>
                <FileUploadCard
                  item={ele}
                  key={index}
                  onDataChange={handleDataChange}
                />
              </>
            );
          })}
      </Box>
    </>
  );
};

export default PdfCard;
