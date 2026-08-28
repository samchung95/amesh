package io.amesh.client;

import java.util.ArrayList;
import java.util.List;

public final class Pagination {
    private Pagination() {}

    public static final class Page<T> {
        private final List<T> items;
        private final String nextCursor;

        public Page(List<T> items, String nextCursor) {
            this.items = List.copyOf(items);
            this.nextCursor = nextCursor;
        }

        public List<T> items() { return items; }
        public String nextCursor() { return nextCursor; }
    }

    @FunctionalInterface
    public interface Loader<T> {
        Page<T> load(String cursor) throws Exception;
    }

    public static <T> List<T> collect(Loader<T> loader) throws Exception {
        List<T> items = new ArrayList<>();
        String cursor = null;
        do {
            Page<T> page = loader.load(cursor);
            items.addAll(page.items());
            cursor = page.nextCursor();
        } while (cursor != null && !cursor.isEmpty());
        return List.copyOf(items);
    }
}
