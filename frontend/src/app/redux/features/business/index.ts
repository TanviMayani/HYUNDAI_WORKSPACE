import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { axiosBaseQuery } from "../../../utils/helper";

export const businessProfileApis = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: ``,
  }),
  reducerPath: "business",
  endpoints: (builder) => ({
    getBusinessProfile: builder.query<any, any>({
      query: () => {
        return {
          method: "get",
          url: `${COMMON_API_URL.getBusiness}`,
        };
      },
      //providesTags: ['Profile']
    }),
    updateBusinessProfile: builder.mutation({
      query: ({ data }) => {
        return {
          url: `${COMMON_API_URL.getBusiness}`,
          method: "patch",
          data: { ...data },
        };
      },
    }),
    
  }),
});
export const {
  useGetBusinessProfileQuery,
  useUpdateBusinessProfileMutation,
} = businessProfileApis;
