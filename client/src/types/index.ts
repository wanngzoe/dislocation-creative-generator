export interface CreativeInput {
  targetUser: string;
  dislocationType: string;
  description: string;
  reference?: string;
  industry?: string;
  count: number;
}

export interface Creative {
  id: string;
  sceneDescription: string;
  narration: string;
}

export interface GenerateRequest {
  input: CreativeInput;
}

export interface GenerateResponse {
  creatives: Creative[];
  success: boolean;
  error?: string;
}
