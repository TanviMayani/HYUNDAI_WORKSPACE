import React from "react";
import DropzoneS3Uploader from "react-dropzone-s3-uploader";
const mainConfig = {
  bucketName: import.meta.env.BUCKET_NAME || "bsl-idp",
  region: import.meta.env.VITE_AWS_REGION,
  accessKeyId: import.meta.env.VITE_AWS_ACCESS_ID,
  secretAccessKey: import.meta.env.VITE_AWS_SECRET_KEY,
  dirName: "photos",
  ACL: "public-read",
};
const S3Uploader = () => {
  const handleFinishedUpload = (info) => {
    // console.log("");
  };
  return (
    <DropzoneS3Uploader
      multiple={true}
      s3Url={`https://${mainConfig.bucketName}.s3.amazonaws.com/`}
      onFinish={handleFinishedUpload}
      {...mainConfig}
    />
  );
};

export default S3Uploader;
