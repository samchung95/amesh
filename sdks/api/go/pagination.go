package ameshclient

import "context"

type Page[T any] struct {
	Items      []T
	NextCursor string
}

type PageLoader[T any] func(context.Context, string) (Page[T], error)

func CollectPages[T any](ctx context.Context, load PageLoader[T]) ([]T, error) {
	var all []T
	var cursor string
	for {
		page, err := load(ctx, cursor)
		if err != nil {
			return nil, err
		}
		all = append(all, page.Items...)
		cursor = page.NextCursor
		if cursor == "" {
			return all, nil
		}
	}
}
