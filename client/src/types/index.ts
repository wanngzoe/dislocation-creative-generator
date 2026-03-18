export interface CreativeInput {
  targetUser: string;
  dislocationType: string;
  hook: string;
  material: string;
  reference?: string;
  industry?: string;
  count: number;
}

export interface Creative {
  id: string;
  hookScene: string;
  hookNarration: string;
  materialScene: string;
  materialNarration: string;
  transition: string;
}

export interface GenerateRequest {
  input: CreativeInput;
}

export interface GenerateResponse {
  creatives: Creative[];
  success: boolean;
  error?: string;
}
