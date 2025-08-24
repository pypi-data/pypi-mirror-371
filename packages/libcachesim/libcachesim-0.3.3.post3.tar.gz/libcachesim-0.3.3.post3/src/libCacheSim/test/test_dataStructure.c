//
// Created by Juncheng Yang on 11/24/24.
//

#include "common.h"
#include "dataStructure/hashtable/chainedHashTableV2.h"
#include "dataStructure/hashtable/hashtable.h"

void test_chained_hashtable_v2(gconstpointer user_data) {
  set_rand_seed(rand());
  hashtable_t *hashtable = create_chained_hashtable_v2(2);
  request_t *req = new_request();
  for (int i = 0; i < 16; i++) {
    req->obj_id = i;
    chained_hashtable_insert_v2(hashtable, req);
  }

  bool seen_bit[16] = {false};
  for (int i = 0; i < 1280; i++) {
    cache_obj_t *obj = chained_hashtable_rand_obj_v2(hashtable);
    if (!seen_bit[obj->obj_id]) {
      printf("object %llu at %d\n", (unsigned long long)obj->obj_id, i);
    }
    seen_bit[obj->obj_id] = true;
  }

  print_chained_hashtable_v2(hashtable);
  // cache_obj_t *obj = chained_hashtable_rand_obj_v2(hashtable);
  // printf("random object %lu\n", obj->obj_id);

  // clean up
  free_request(req);
  free_chained_hashtable_v2(hashtable);
}

int main(int argc, char *argv[]) {
  g_test_init(&argc, &argv, NULL);

  g_test_add_data_func("/libCacheSim/test_chained_hashtable_v2", NULL,
                       test_chained_hashtable_v2);

  return g_test_run();
}
