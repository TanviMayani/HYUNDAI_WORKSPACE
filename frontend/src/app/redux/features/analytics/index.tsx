import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { axiosBaseQuery } from "../../../utils/helper";

export const analyticsApi = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: ``,
  }),
  reducerPath: "analytics",
  keepUnusedDataFor: 5,
  refetchOnMountOrArgChange: true,
  endpoints: (builder) => ({
    getAnalytics: builder.query<any, any>({
      query: () => {
        return {
          method: "get",
          url: `${COMMON_API_URL.getAnalytics}`,
        };
      },
      //providesTags: ['Profile']
    }),
  }),
});
export const { useGetAnalyticsQuery } = analyticsApi;
