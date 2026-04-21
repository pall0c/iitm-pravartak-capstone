import axios from "axios";

import type { AuthorOption, QueryRequest, QueryResponse } from "@/lib/api-types";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const fetchAuthors = async (): Promise<AuthorOption[]> => {
  const response = await api.get<AuthorOption[]>("/api/v1/authors");
  return response.data;
};

export const submitQuery = async (
  payload: QueryRequest,
): Promise<QueryResponse> => {
  const response = await api.post<QueryResponse>("/api/v1/query", payload);
  return response.data;
};

export { axios };
