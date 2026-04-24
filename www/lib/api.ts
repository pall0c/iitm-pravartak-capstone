import axios from "axios";

import type {
  AuthorOption,
  QueryRequest,
  QueryResponse,
} from "@/lib/api-types";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    Accept: "application/json",
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
  const response = await api.post<QueryResponse>("/api/v1/query", payload, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
  return response.data;
};

export { axios };
