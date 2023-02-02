#!/usr/bin/python3

from random import randint
from typing import List

array = []

for i in range(16):
    array.append(randint(0, 128))

print("before sort")
print(array)

def conquer(arr: List[int], low: int, high: int) -> int:
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]

    return i + 1

def quick_sort(arr: List[int], low: int, high: int):
    if (low < high):
        index = conquer(arr, low, high)
        quick_sort(arr, low, index - 1)
        quick_sort(arr, index + 1, high)

array_len = len(array)
quick_sort(array, 0, array_len - 1)

print("after sort")
print(array)