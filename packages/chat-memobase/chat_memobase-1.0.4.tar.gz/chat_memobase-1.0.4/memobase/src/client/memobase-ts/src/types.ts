import { z } from 'zod';

// HttpUrl 类型
export const HttpUrl = z.string().url();
export type HttpUrl = z.infer<typeof HttpUrl>;

// BlobType 枚举
export const BlobType = z.enum(['chat', 'doc', 'image', 'code', 'transcript']);
export type BlobType = z.infer<typeof BlobType>;

// OpenAICompatibleMessage 类型
export const OpenAICompatibleMessage = z.object({
  role: z.enum(['user', 'assistant']),
  content: z.string(),
  alias: z.string().optional(),
  created_at: z.string().optional(),
});
export type OpenAICompatibleMessage = z.infer<typeof OpenAICompatibleMessage>;

// TranscriptStamp 类型
export const TranscriptStamp = z.object({
  content: z.string(),
  start_timestamp_in_seconds: z.number(),
  end_time_timestamp_in_seconds: z.number().optional(),
  speaker: z.string().optional(),
});
export type TranscriptStamp = z.infer<typeof TranscriptStamp>;

// BaseBlob 类型
export const BaseBlob = z.object({
  type: BlobType,
  fields: z.record(z.unknown()).optional(),
  created_at: z.date().optional(),
});
export type BaseBlob = z.infer<typeof BaseBlob>;

// ChatBlob 类型
export const ChatBlob = BaseBlob.extend({
  type: z.literal('chat'),
  messages: z.array(OpenAICompatibleMessage),
});
export type ChatBlob = z.infer<typeof ChatBlob>;

// DocBlob 类型
export const DocBlob = BaseBlob.extend({
  type: z.literal('doc'),
  content: z.string(),
});
export type DocBlob = z.infer<typeof DocBlob>;

// CodeBlob 类型
export const CodeBlob = BaseBlob.extend({
  type: z.literal('code'),
  content: z.string(),
  language: z.string().optional(),
});
export type CodeBlob = z.infer<typeof CodeBlob>;

// ImageBlob 类型
export const ImageBlob = BaseBlob.extend({
  type: z.literal('image'),
  url: z.string().optional(),
  base64: z.string().optional(),
});
export type ImageBlob = z.infer<typeof ImageBlob>;

// TranscriptBlob 类型
export const TranscriptBlob = BaseBlob.extend({
  type: z.literal('transcript'),
  transcripts: z.array(TranscriptStamp),
});
export type TranscriptBlob = z.infer<typeof TranscriptBlob>;

// Blob 类型
export const Blob = z.union([ChatBlob, DocBlob, CodeBlob, ImageBlob, TranscriptBlob]);
export type Blob = z.infer<typeof Blob>;

// UserProfile 类型
export const UserProfile = z.object({
  id: z.string(),
  content: z.string(),
  topic: z.string(),
  sub_topic: z.string(),
  created_at: z.date(),
  updated_at: z.date(),
});
export type UserProfile = z.infer<typeof UserProfile>;

// BaseResponse 类型
export const BaseResponse = <T>(dataSchema: z.ZodType<T, any, any>) =>
  z.object({
    data: dataSchema.optional(),
    errmsg: z.string(),
    errno: z.number(),
  });
export type BaseResponse<T = any> = z.infer<ReturnType<typeof BaseResponse<T>>>;

// IdResponse 类型
export const IdResponse = z.object({
  id: z.string(),
});
export type IdResponse = z.infer<typeof IdResponse>;

// ProfileResponse 类型
export const ProfileResponse = z.object({
  profiles: z.array(
    z.object({
      id: z.string(),
      content: z.string(),
      attributes: z.object({
        topic: z.string(),
        sub_topic: z.string(),
      }),
      created_at: z.string(),
      updated_at: z.string(),
    }),
  ),
});
export type ProfileResponse = z.infer<typeof ProfileResponse>;

// UserEvent 类型
export const UserEvent = z.object({
  id: z.string(),
  event_data: z
    .object({
      profile_delta: z
        .array(
          z.object({
            content: z.string(),
            attributes: z.record(z.any()).optional(),
          }),
        )
        .optional(),
      event_tip: z.string().optional().nullable(),
      event_tags: z
        .array(
          z.object({
            tag: z.string(),
            value: z.string(),
          }),
        )
        .optional()
        .nullable(),
    })
    .optional(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
export type UserEvent = z.infer<typeof UserEvent>;

// UserGistEvent 类型
export const UserGistEvent = z.object({
  id: z.string(),
  gist_data: z
    .object({
      content: z.string(),
    })
    .optional(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
  similarity: z.number().optional(),
});
export type UserGistEvent = z.infer<typeof UserGistEvent>;

// EventResponse 类型
export const EventResponse = z.object({
  events: z.array(UserEvent),
});
export type EventResponse = z.infer<typeof EventResponse>;

// GistEventResponse 类型
export const GistEventResponse = z.object({
  events: z.array(UserGistEvent),
});
export type GistEventResponse = z.infer<typeof GistEventResponse>;

// ContextResponse 类型
export const ContextResponse = z.object({
  context: z.string(),
});
export type ContextResponse = z.infer<typeof ContextResponse>;

// GetConfigResponse 类型
export const GetConfigResponse = z.object({
  profile_config: z.string(),
});
export type GetConfigResponse = z.infer<typeof GetConfigResponse>;

// ProjectUser 类型
export const ProjectUser = z.object({
  id: z.string(),
  project_id: z.string(),
  profile_count: z.number(),
  event_count: z.number(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
export type ProjectUser = z.infer<typeof ProjectUser>;

// GetProjectUsersResponse 类型
export const GetProjectUsersResponse = z.object({
  users: z.array(ProjectUser),
  count: z.number(),
});
export type GetProjectUsersResponse = z.infer<typeof GetProjectUsersResponse>;

// GetProjectUsageItemResponse 类型
export const GetProjectUsageItemResponse = z.object({
  date: z.coerce.date(),
  total_insert: z.number(),
  total_success_insert: z.number(),
  total_input_token: z.number(),
  total_output_token: z.number(),
});
export type GetProjectUsageItemResponse = z.infer<typeof GetProjectUsageItemResponse>;
