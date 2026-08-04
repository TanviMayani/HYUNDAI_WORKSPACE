// eslint-disable-next-line no-undef
import AWS from "aws-sdk";
import { Buffer } from "buffer";
import toast from "react-hot-toast";
window.Buffer = window.Buffer || Buffer;

const mainconfig = {
  bucketName: "bsl-idp",
  region: import.meta.env.VITE_AWS_REGION,
  accessKeyId: import.meta.env.VITE_AWS_ACCESS_ID,
  secretAccessKey: import.meta.env.VITE_AWS_SECRET_KEY,
  dirName: "photos",
  ACL: "public-read",
};
const getS3Object = () => {
  return new AWS.S3({ region: "us-west-2" });
};

export const s3UriToHttpsUrl = (s3Uri) => {
  const match = s3Uri.match(/^s3:\/\/([^/]+)\/(.+)$/);
  if (match) {
    const bucketName = match[1];
    const pathWithinBucket = match[2];
    const awsRegion = mainconfig.region;
    const httpsUrl = `https://${bucketName}.s3.${awsRegion}.amazonaws.com/${pathWithinBucket}`;
    return httpsUrl;
  } else {
    return null;
  }
};

window.getS3Object = getS3Object;

export const uploadToS3 = (file, dirName, mimeType, handleLoading) => {
  return new Promise((resolve, reject) => {
    const config = dirName ? { ...mainconfig, dirName } : { ...mainconfig };
    if (config.bucketName && config.region && config.secretAccessKey) {
      const s3 = new AWS.S3(config);
      const params = {
        Bucket: config.bucketName,
        Key: config.dirName ? `${config.dirName}/${file.name}` : file.name,
        Body: file,
        ContentType: mimeType,
      };
      const request = s3?.upload(params);
      request.on("httpUploadProgress", (progress) => {
        const percent = Math.round((progress?.loaded / progress?.total) * 100);
        handleLoading(percent);
      });
      request.send((err, data) => {
        if (err) {
          reject(err);
        } else {
          resolve(data);
        }
      });
    }
  });
};

export const multipleFileUpload = (files, dirName, mimeType, handleLoading) => {
  return new Promise((resolve, reject) => {
    const config = dirName ? { ...mainconfig, dirName } : { ...mainconfig };
    if (config.bucketName && config.region && config.secretAccessKey) {
      const s3 = new AWS.S3(config);
      let promises = [];
      for (var i = 0; i < files.length; i++) {
        var file = files[i];
        const params = {
          Bucket: config.bucketName,
          Key: config.dirName ? `${config.dirName}/${file.name}` : file.name,
          Body: file,
          ContentType: mimeType,
        };
        const newPromise = s3.upload({ ...params, file }).promise();
        promises.push(newPromise);
      }
      Promise.all(promises)
        .then(function (data) {
          toast.success("uploaded");
          handleLoading(100);
          resolve(data);
        })
        .catch(function (err) {
          toast.error("failed");
          reject(err);
        });
    }
  });
};
