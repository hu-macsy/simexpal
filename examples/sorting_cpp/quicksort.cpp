#include <iostream>
#include <vector>
#include <fstream>
#include <string>

int block_size = 16;
void (*block_algo)(std::vector<int>&, int, int);

void print_vector(std::vector<int> const &vec){
    for(int i : vec) {
        std::cout << i << std::endl;
    }
    std::cout << std::endl;
}

void insertion_sort(std::vector<int> &vec, int low, int high){
    int key, j;

    if(low < high){
        for (int i = low + 1; i <= high; i++){
            key = vec[i];
            j = i - 1;

            while (j >= low && vec[j] > key){
                vec[j + 1] = vec[j];
                j = j - 1;
            }
            vec[j + 1] = key;
        }
    }
}

void bubble_sort(std::vector<int> &vec, int low, int high){
    int i, j;

    if (low < high){
        for (i = low; i < high; i++){
            for (j = 0; j <= high-i-1; j++){
                if (vec[low + j] > vec[low + j+1])
                    std::swap(vec[low + j], vec[low +j+1]);
            }
        }
    }
}

int partition (std::vector<int> &vec, int low, int high){
    int pivot = vec[high];
    int i = (low - 1);

    for (int j = low; j < high; j++){

        if (vec[j] < pivot) {
            i++;
            std::swap(vec[i], vec[j]);
        }
    }
    std::swap(vec[i + 1], vec[high]);

    return (i + 1);
}

void quick_sort(std::vector<int> &vec, int low, int high){

    if (low < high){
        int pivot = partition(vec, low, high);

        if (pivot - 1 - low < block_size) {
            block_algo(vec, low, pivot - 1);
        } else {
            quick_sort(vec, low, pivot - 1);
        }

        if (high - pivot - 1 < block_size) {
            block_algo(vec, pivot + 1, high);
        } else {
            quick_sort(vec, pivot + 1, high);
        }
    }
}

/*
 * The parameters for the main() have to be in the following order:
 * argv[1]: path to input file
 * argv[2]: (optional) base block algorithm (default: quick_sort, other possible values: insertion_sort, bubble_sort
 *                                anything else will be ignored)
 * argv[3]: (optional) base block size (default: 16)
 */
int main(int argc, char **argv){

    std::ifstream infile( argv[1]);

    std::string block_algo_name = "quick_sort";
    block_algo = &quick_sort;
    if(argc > 2){
        if(std::string(argv[2]) == "insertion_sort"){
            block_algo = &insertion_sort;
            block_algo_name = "insertion_sort";
        }
        else if(std::string(argv[2]) == "bubble_sort"){
            block_algo = &bubble_sort;
            block_algo_name = "bubble_sort";
        }
    }
    if(argc > 3){
        if(std::stoi(argv[3]) > 0) {
            block_size = std::stoi(argv[3]);
        }
    }

    std::vector<int> arr;
    int a;
    while (infile >> a){
        arr.push_back(a);
    }

    quick_sort(arr, 0, arr.size()-1);
    printf("block size: %i \n", block_size);
    printf("block algorithm: %s \n\n", block_algo_name.c_str());
    print_vector(arr);
    return 0;
}
