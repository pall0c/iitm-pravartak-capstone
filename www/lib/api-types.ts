export type AuthorOption = {
  key: string;
  author: string;
  work: string;
};

export type SourceHit = {
  author: string;
  author_key: string;
  work: string;
  source_file: string;
  page: number;
  excerpt: string;
};

export type QueryResponse = {
  answer: string;
  sources: SourceHit[];
};

export type QueryRequest = {
  question: string;
  author_key?: string;
};
