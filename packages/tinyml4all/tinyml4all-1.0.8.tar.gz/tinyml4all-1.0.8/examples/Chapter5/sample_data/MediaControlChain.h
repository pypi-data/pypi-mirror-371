#include <cmath>
#include <iostream>
#include <unistd.h>


namespace math {
    /**
     * Absolute value
     */
    inline float absolute(float x) {
        return x >= 0 ? x : -x;
    }

    /**
     * Alias of max
     */
    inline float largest(float x, float y) {
        return x > y ? x : y;
    }

    /**
     * Alias of min
     */
    inline float least(float x, float y) {
        return x < y ? x : y;
    }

    /**
     * Square root (absolute value)
     */
    inline float sqrt(float x) {
        return std::sqrt(math::absolute(x));
    }

    /**
     * Division (0 safe)
     */
    inline float divide(float n, float d) {
        return math::absolute(d) > 0.000001 ? n / d : n;
    }

    /**
     * Log(1 + abs(x))
     */
    inline float log(float x) {
        return std::log(1 + math::absolute(x));
    }

    /**
     * Exp(abs(x)) with x <= 30
     */
    inline float exp(float x) {
        return math::absolute(x) <= 30 ? std::exp(math::absolute(x)) : 0;
    }
}
namespace np {
    /**
     * Array mean
     */
    float mean(float *array, const uint16_t count) {
        float sum = 0;

        for (uint16_t i = 0; i < count; i++)
            sum += array[i];

        return sum / count;
    }

    /**
     * Array abs mean
     */
    float absmean(float *array, const uint16_t count) {
        float sum = 0;

        for (uint16_t i = 0; i < count; i++)
            sum += abs(array[i]);

        return sum / count;
    }

    /**
     * Array maximum
     */
    float maximum(float *array, const uint16_t count) {
        float maximum = array[0];

        for (uint16_t i = 1; i < count; i++)
            if (array[i] > maximum)
                maximum = array[i];

        return maximum;
    }

    /**
     * Array minimum
     */
    float minimum(float *array, const uint16_t count) {
        float minimum = array[0];

        for (uint16_t i = 1; i < count; i++)
            if (array[i] < minimum)
                minimum = array[i];

        return minimum;
    }
}


// pre-processing chain
namespace internals {
    #pragma once
#include <cstring>

namespace math {
    /**
     * Absolute value
     */
    inline float absolute(float x) {
        return x >= 0 ? x : -x;
    }

    /**
     * Alias of max
     */
    inline float largest(float x, float y) {
        return x > y ? x : y;
    }

    /**
     * Alias of min
     */
    inline float least(float x, float y) {
        return x < y ? x : y;
    }

    /**
     * Square root (absolute value)
     */
    inline float sqrt(float x) {
        return std::sqrt(math::absolute(x));
    }

    /**
     * Division (0 safe)
     */
    inline float divide(float n, float d) {
        return math::absolute(d) > 0.000001 ? n / d : n;
    }

    /**
     * Log(1 + abs(x))
     */
    inline float log(float x) {
        return std::log(1 + math::absolute(x));
    }

    /**
     * Exp(abs(x)) with x <= 30
     */
    inline float exp(float x) {
        return math::absolute(x) <= 30 ? std::exp(math::absolute(x)) : 0;
    }
}

/**
 * A classification chain for tabular data
 */
namespace tinyml4all {
    /**
 * Handle all inputs of the chain
 * (from outside and internal)
 */
class Input {
    public:
        
            float _Tz3Q7P__mz;
        
            float _PSawsX__mx;
        
            float _aGTzid__my;
        

        /**
         * Copy from other input
         */
        void copyFrom(Input& other) {
            
                _Tz3Q7P__mz = other._Tz3Q7P__mz;
            
                _PSawsX__mx = other._PSawsX__mx;
            
                _aGTzid__my = other._aGTzid__my;
            
        }
};
    /**
 * Handle all outputs
 * TODO
 */
 class Output {
    public:
        struct {
            float value;
        } regression;
        struct {
            uint8_t idx;
            uint8_t prevIdx;
            float confidence;
            float prevConfidence;
            String label;
            String prevLabel;
        } classification;

        Output() {
            classification.idx = 0;
            classification.confidence = 0;
        }
 };
    class Classmap {
    public:

        /**
         * Get label for index
         */
        String get(int8_t idx) {
            
                switch (idx) {
                    
                        case 0: return "next";
                    
                        case 1: return "raise";
                    
                        case 2: return "tap";
                    
                    default: return "Unknown";
                }
            

            return String(idx);
        }
};

    // processing blocks
    
    /**
 * Scale(method=minmax, offsets=[-400. -400. -400.], scales=[799.987793 709.49707  799.987793])
 */
class _G2ruJf__scale_133891439961680_8368214997605 {
    public:

        void operator()(Input& input, Output& output) {
            

            
                
                    input._PSawsX__mx = (input._PSawsX__mx - -400.0f) * 0.0012500190737285413f;
                
                    input._aGTzid__my = (input._aGTzid__my - -400.0f) * 0.0014094490904662932f;
                
                    input._Tz3Q7P__mz = (input._Tz3Q7P__mz - -400.0f) * 0.0012500190737285413f;
                
            

            
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }
};
    

    /**
     * Chain class
     * Chain(blocks=[Scale(method=minmax, offsets=[-400. -400. -400.], scales=[799.987793 709.49707  799.987793])])
     */
     class PreprocessingChain {
        public:
            Input input;
            Output output;
            Classmap classmap;

            /**
 * Transform Input
 */
bool operator()(const Input& input) {
    return operator()(input._PSawsX__mx, input._aGTzid__my, input._Tz3Q7P__mz);
}

/**
 * Transform array input
 */
bool operator()(float *inputs) {
    return operator()(inputs[0], inputs[1], inputs[2]);
}

/**
 * Transform const array input
 */
bool operator()(const float *inputs) {
    return operator()(inputs[0], inputs[1], inputs[2]);
}

            /**
             * Transform variadic input
             */
            bool operator()(const float _PSawsX__mx, const float _aGTzid__my, const float _Tz3Q7P__mz) {
                // assign variables to input
                
                    input._PSawsX__mx = _PSawsX__mx;
                
                    input._aGTzid__my = _aGTzid__my;
                
                    input._Tz3Q7P__mz = _Tz3Q7P__mz;
                

                // run blocks
                
                    // Scale(method=minmax, offsets=[-400. -400. -400.], scales=[799.987793 709.49707  799.987793])
                    block1(input, output);

                    if (!block1.isReady())
                        return false;
                

                output.classification.label = classmap.get(output.classification.idx);

                return true;
            }

        protected:
            
                // Scale(method=minmax, offsets=[-400. -400. -400.], scales=[799.987793 709.49707  799.987793])
                _G2ruJf__scale_133891439961680_8368214997605 block1;
            
    };
}
}


namespace tinyml4all {
    /**
 * Handle all inputs of the chain
 * (from outside and internal)
 */
class Input {
    public:
        
            float _kIX8Zh__momentsmaxmx;
        
            float _SxHu89__momentsmaxabsmy;
        
            float _XiOuCe__momentsminmx;
        
            float _Znwbtu__momentsstdmz;
        
            float _FkO1dy__momentsmeanmy;
        
            float _PSawsX__mx;
        
            float _ypwfnt__momentsmaxabsmx;
        
            float _b2Fi2p__momentsminabsmz;
        
            float _Tz3Q7P__mz;
        
            float _x2BxiN__momentsmeanabsmy;
        
            float _clg7v2__momentsmaxabsmz;
        
            float _Oic8kL__momentsminabsmy;
        
            float _15tt2v__momentsmeanabsmz;
        
            float _km4spH__peaksmz;
        
            float _F5bOdo__momentsstdmy;
        
            float _zZmGqV__count_above_meanmx;
        
            float _hqsjUF__momentsmeanmz;
        
            float _vI9LHD__momentsstdmx;
        
            float _HRgdF2__momentsmaxmy;
        
            float _fz7hE5__count_above_meanmy;
        
            float _9XogdU__autocorrelationmx;
        
            float _IknBSj__momentsminabsmx;
        
            float _V7ILZq__count_above_meanmz;
        
            float _ZP45RY__peaksmy;
        
            float _082CHh__momentsminmz;
        
            float _u0yBgY__autocorrelationmz;
        
            float _jWd98P__peaksmx;
        
            float _jSiICE__momentsmeanmx;
        
            float _lnNby7__momentsmeanabsmx;
        
            float _aGTzid__my;
        
            float _j861DZ__autocorrelationmy;
        
            float _EklLmr__momentsmaxmz;
        
            float _SalQct__momentsminmy;
        

        /**
         * Copy from other input
         */
        void copyFrom(Input& other) {
            
                _kIX8Zh__momentsmaxmx = other._kIX8Zh__momentsmaxmx;
            
                _SxHu89__momentsmaxabsmy = other._SxHu89__momentsmaxabsmy;
            
                _XiOuCe__momentsminmx = other._XiOuCe__momentsminmx;
            
                _Znwbtu__momentsstdmz = other._Znwbtu__momentsstdmz;
            
                _FkO1dy__momentsmeanmy = other._FkO1dy__momentsmeanmy;
            
                _PSawsX__mx = other._PSawsX__mx;
            
                _ypwfnt__momentsmaxabsmx = other._ypwfnt__momentsmaxabsmx;
            
                _b2Fi2p__momentsminabsmz = other._b2Fi2p__momentsminabsmz;
            
                _Tz3Q7P__mz = other._Tz3Q7P__mz;
            
                _x2BxiN__momentsmeanabsmy = other._x2BxiN__momentsmeanabsmy;
            
                _clg7v2__momentsmaxabsmz = other._clg7v2__momentsmaxabsmz;
            
                _Oic8kL__momentsminabsmy = other._Oic8kL__momentsminabsmy;
            
                _15tt2v__momentsmeanabsmz = other._15tt2v__momentsmeanabsmz;
            
                _km4spH__peaksmz = other._km4spH__peaksmz;
            
                _F5bOdo__momentsstdmy = other._F5bOdo__momentsstdmy;
            
                _zZmGqV__count_above_meanmx = other._zZmGqV__count_above_meanmx;
            
                _hqsjUF__momentsmeanmz = other._hqsjUF__momentsmeanmz;
            
                _vI9LHD__momentsstdmx = other._vI9LHD__momentsstdmx;
            
                _HRgdF2__momentsmaxmy = other._HRgdF2__momentsmaxmy;
            
                _fz7hE5__count_above_meanmy = other._fz7hE5__count_above_meanmy;
            
                _9XogdU__autocorrelationmx = other._9XogdU__autocorrelationmx;
            
                _IknBSj__momentsminabsmx = other._IknBSj__momentsminabsmx;
            
                _V7ILZq__count_above_meanmz = other._V7ILZq__count_above_meanmz;
            
                _ZP45RY__peaksmy = other._ZP45RY__peaksmy;
            
                _082CHh__momentsminmz = other._082CHh__momentsminmz;
            
                _u0yBgY__autocorrelationmz = other._u0yBgY__autocorrelationmz;
            
                _jWd98P__peaksmx = other._jWd98P__peaksmx;
            
                _jSiICE__momentsmeanmx = other._jSiICE__momentsmeanmx;
            
                _lnNby7__momentsmeanabsmx = other._lnNby7__momentsmeanabsmx;
            
                _aGTzid__my = other._aGTzid__my;
            
                _j861DZ__autocorrelationmy = other._j861DZ__autocorrelationmy;
            
                _EklLmr__momentsmaxmz = other._EklLmr__momentsmaxmz;
            
                _SalQct__momentsminmy = other._SalQct__momentsminmy;
            
        }
};
    /**
 * Handle all outputs
 * TODO
 */
 class Output {
    public:
        struct {
            float value;
        } regression;
        struct {
            uint8_t idx;
            uint8_t prevIdx;
            float confidence;
            float prevConfidence;
            String label;
            String prevLabel;
        } classification;

        Output() {
            classification.idx = 0;
            classification.confidence = 0;
        }
 };
    class Classmap {
    public:

        /**
         * Get label for index
         */
        String get(int8_t idx) {
            
                switch (idx) {
                    
                        case 0: return "next";
                    
                        case 1: return "raise";
                    
                        case 2: return "tap";
                    
                    default: return "Unknown";
                }
            

            return String(idx);
        }
};

    // windowing
    class Window {
    public:
        const uint16_t length = 76;
        float data[3][76];

        /**
         * Constructor
         */
        Window() : head(0) {
        }

        /**
         * Feed data
         */
        void operator()(Input& input) {
            if (isReady())
                shift();

            
                data[0][head] = input._PSawsX__mx;
            
                data[1][head] = input._aGTzid__my;
            
                data[2][head] = input._Tz3Q7P__mz;
            

            head++;
        }

        /**
         * Test if new chunk of data is available
         */
        bool isReady() {
            return head >= 76;
        }

    protected:
        uint32_t head;

        void shift() {
            // cap head
            if (head >= 76)
                head = 76;

            // shift data to the left by 19
            for (uint16_t ax = 0; ax < 3; ax++) {
                for (uint16_t i = 0; i < 57; i++)
                    data[ax][i] = data[ax][i + 19];
            }

            head = 76 - 19;
        }
};

    // ovr
    /**
 * Binary classification chain
 * Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:max(mx)', 'moments:mean(mx)', 'moments:min(abs(mx))', 'moments:max(abs(mx))', 'moments:mean(abs(mx))', 'moments:max(my)', 'moments:mean(my)', 'moments:min(abs(my))', 'moments:max(abs(my))', 'moments:max(mz)', 'moments:mean(mz)', 'moments:min(abs(mz))', 'moments:max(abs(mz))', 'peaks(mx)', 'peaks(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
 */
 // feature extractors

/**
 * Moments()
 */
class _cStaZJ__moments_133891436519952_8368214782497 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: mx
                extract(window.data[0] + window.length - 76, &(input._XiOuCe__momentsminmx), &(input._kIX8Zh__momentsmaxmx), &(input._jSiICE__momentsmeanmx), &(input._IknBSj__momentsminabsmx), &(input._ypwfnt__momentsmaxabsmx), &(input._lnNby7__momentsmeanabsmx), &(input._vI9LHD__momentsstdmx) );
            
                // dimension: my
                extract(window.data[1] + window.length - 76, &(input._SalQct__momentsminmy), &(input._HRgdF2__momentsmaxmy), &(input._FkO1dy__momentsmeanmy), &(input._Oic8kL__momentsminabsmy), &(input._SxHu89__momentsmaxabsmy), &(input._x2BxiN__momentsmeanabsmy), &(input._F5bOdo__momentsstdmy) );
            
                // dimension: mz
                extract(window.data[2] + window.length - 76, &(input._082CHh__momentsminmz), &(input._EklLmr__momentsmaxmz), &(input._hqsjUF__momentsmeanmz), &(input._b2Fi2p__momentsminabsmz), &(input._clg7v2__momentsmaxabsmz), &(input._15tt2v__momentsmeanabsmz), &(input._Znwbtu__momentsstdmz) );
            
        }

    protected:

        void extract(float *array, float *minimum, float *maximum, float *average, float *absminimum, float *absmaximum, float *absaverage, float *stddev) {
            const float inverseCount = 0.013157894736842105f;
            float sum = 0;
            float absum = 0;
            float m = 3.402823466e+38F;
            float M = -3.402823466e+38F;
            float absm = 3.402823466e+38F;
            float absM = 0;

            // first pass (min, max, mean)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float a = math::absolute(v);

                sum += v;
                absum += a;

                if (v < m) m = v;
                if (v > M) M = v;
                if (a < absm) absm = a;
                if (a > absM) absM = a;
            }

            const float mean = sum * inverseCount;
            float var = 0;
            float skew = 0;
            float kurtosis = 0;

            *minimum = m;
            *maximum = M;
            *average = mean;
            *absminimum = absm;
            *absmaximum = absM;
            *absaverage = absum * inverseCount;

            // second pass (std, skew, kurtosis)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float d = v - mean;
                const float s = pow(d, 3);

                var += d * d;
                //skew += s;
                //kurtosis += s * d; // a.k.a. d^4
            }

            *stddev = std::sqrt(var * inverseCount);
            //*skew = sk / pow(var, 1.5) * inverseCount;
            //*kurtosis = kurt / pow(var, 2) * inverseCount;
        }
};

/**
 * Autocorrelation(lag=1)
 */
class _RphGfu__autocorrelation_133891436522256_8368214782641 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._9XogdU__autocorrelationmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._j861DZ__autocorrelationmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._u0yBgY__autocorrelationmz));
            
        }

    protected:

        void extract(float *array, float *autocorrelation) {
            const float mean = np::mean(array, 76);
            float num = 0;
            float den = (array[0] - mean) * (array[0] - mean);

            // second pass (autocorrelation)
            for (uint16_t i = 1; i < 76; i++) {
                const float current = array[i - 1] - mean;
                const float next = array[i] - mean;

                num += current * next;
                den += next * next;
            }

            *autocorrelation = num / den;
        }
};

/**
 * Peaks(magnitude=0.1)
 */
class _za9viD__peaks_133891439961232_8368214997577 {
    public:

        void operator()(Window& window, Input& input) {
            
        }

    protected:

        void extract(float *array, float *peaksCount) {
            const float thres = (np::maximum(array, 76) - np::minimum(array, 76)) * 0.1f;
            uint16_t peaks = 0;

            for (uint16_t i = 1; i < 76 - 1; i++) {
                const float prev = array[i - 1];
                const float curr = array[i];
                const float next = array[i + 1];

                // check if peak
                if (math::absolute(curr - prev) > thres && math::absolute(curr - next) > thres)
                    peaks++;
            }

            *peaksCount = peaks / 74.0f;
        }
};

/**
 * CountAboveMean()
 */
class _0vEWhV__countabovemean_133891436527440_8368214782965 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._zZmGqV__count_above_meanmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._fz7hE5__count_above_meanmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._V7ILZq__count_above_meanmz));
            
        }

    protected:

        void extract(float *array, float *countAboveMean) {
            const float mean = np::mean(array, 76);
            uint32_t count = 0;

            // second pass (count)
            for (uint16_t i = 0; i < 76; i++) {
                if (array[i] > mean)
                    count++;
            }

            *countAboveMean = count / 76f;
        }
};


// ovr block

class _X6CMiC__select_133891444837200_8368215302325 {
    public:

        /**
         * Perform feature selection
         */
        void operator()(Input& input, Output& output) {
            // nothing to do, feature selection is only needed in Python
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }
};

/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=957146846)
 */
class _D96qjV__decisiontree_133891434844112_8368214677757 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._ypwfnt__momentsmaxabsmx < 0.4906538426876068f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9170305676855895;
    return;

    }
    else {
        
    if (input._hqsjUF__momentsmeanmz < 0.3495611995458603f) {
        
    if (input._kIX8Zh__momentsmaxmx < 0.49510185420513153f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.08296943231441048;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9170305676855895;
    return;

    }

    }
    else {
        
    if (input._ypwfnt__momentsmaxabsmx < 0.49267566204071045f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9170305676855895;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9170305676855895;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1307457104)
 */
class _yPQy5b__decisiontree_133891433446736_8368214590421 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._ypwfnt__momentsmaxabsmx < 0.4906538426876068f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8908296943231441;
    return;

    }
    else {
        
    if (input._kIX8Zh__momentsmaxmx < 0.49291980266571045f) {
        
    if (input._jSiICE__momentsmeanmx < 0.45337074995040894f) {
        
    if (input._lnNby7__momentsmeanabsmx < 0.4054284989833832f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.1091703056768559;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.1091703056768559;
    return;

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8908296943231441;
    return;

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8908296943231441;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=902715607)
 */
class _fXJh0F__decisiontree_133891433186832_8368214574177 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._b2Fi2p__momentsminabsmz < 0.215358205139637f) {
        
    if (input._Oic8kL__momentsminabsmy < 0.4724200814962387f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }
    else {
        
    if (input._HRgdF2__momentsmaxmy < 0.6238859593868256f) {
        
    if (input._EklLmr__momentsmaxmz < 0.3739452213048935f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }

    }
    else {
        
    if (input._lnNby7__momentsmeanabsmx < 0.37455548346042633f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.07423580786026202;
    return;

    }

    }

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925764192139738;
    return;

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=859188304)
 */
class _SWRyJ0__decisiontree_133891434853264_8368214678329 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._EklLmr__momentsmaxmz < 0.4417639374732971f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9170305676855895;
    return;

    }
    else {
        
    if (input._b2Fi2p__momentsminabsmz < 0.08773937448859215f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9170305676855895;
    return;

    }
    else {
        
    if (input._clg7v2__momentsmaxabsmz < 0.4511711299419403f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.08296943231441048;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9170305676855895;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=989112565)
 */
class _LCphHm__decisiontree_133891433740176_8368214608761 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._IknBSj__momentsminabsmx < 0.15242999792099f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }
    else {
        
    if (input._IknBSj__momentsminabsmx < 0.38995955884456635f) {
        
    if (input._EklLmr__momentsmaxmz < 0.4067368656396866f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }
    else {
        
    if (input._kIX8Zh__momentsmaxmx < 0.47861447930336f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.11353711790393013;
    return;

    }

    }

    }
    else {
        
    if (input._IknBSj__momentsminabsmx < 0.40668344497680664f) {
        
    if (input._ypwfnt__momentsmaxabsmx < 0.43978026509284973f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};

class _V9XrW1__randomforest_133891461064848_8368216316553 {
    public:
        void operator()(Input& input, Output& output) {
            Output treeOutput;
            float scores[2] = { 0 };

            // iterate over trees
            
                tree1(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree2(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree3(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree4(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree5(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            

            // get output with highest vote
            output.classification.idx = 0;
            output.classification.confidence = scores[0];

            for (uint8_t i = 1; i < 2; i++) {
                if (scores[i] > output.classification.confidence) {
                    output.classification.idx = i;
                    output.classification.confidence = scores[i];
                }
            }
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }

    protected:
        
            _D96qjV__decisiontree_133891434844112_8368214677757 tree1;
        
            _yPQy5b__decisiontree_133891433446736_8368214590421 tree2;
        
            _fXJh0F__decisiontree_133891433186832_8368214574177 tree3;
        
            _SWRyJ0__decisiontree_133891434853264_8368214678329 tree4;
        
            _LCphHm__decisiontree_133891433740176_8368214608761 tree5;
        
};


// chain
class _LDQLSZ__binarychain_133891439963664_8368214997729 {
    public:

    _LDQLSZ__binarychain_133891439963664_8368214997729() : ready(false) {

    }

    void operator()(Window& window, Input& input, Output& output) {
        extractFeatures(window, input);

        // ovr
        
            block1(input, output);

            if (!block1.isReady()) {
                ready = false;
                return;
            }
        
            block2(input, output);

            if (!block2.isReady()) {
                ready = false;
                return;
            }
        

        ready = true;
    }

    bool isReady() {
        return ready;
    }

    protected:
        bool ready;

        
            _cStaZJ__moments_133891436519952_8368214782497 extr1;
        
            _RphGfu__autocorrelation_133891436522256_8368214782641 extr2;
        
            _za9viD__peaks_133891439961232_8368214997577 extr3;
        
            _0vEWhV__countabovemean_133891436527440_8368214782965 extr4;
        

        
            // Select(columns=['moments:max(mx)', 'moments:mean(mx)', 'moments:min(abs(mx))', 'moments:max(abs(mx))', 'moments:mean(abs(mx))', 'moments:max(my)', 'moments:mean(my)', 'moments:min(abs(my))', 'moments:max(abs(my))', 'moments:max(mz)', 'moments:mean(mz)', 'moments:min(abs(mz))', 'moments:max(abs(mz))', 'peaks(mx)', 'peaks(mz)'])
            _X6CMiC__select_133891444837200_8368215302325 block1;
        
            // RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)
            _V9XrW1__randomforest_133891461064848_8368216316553 block2;
        

        void extractFeatures(Window& window, Input& input) {
            
                extr1(window, input);
            
                extr2(window, input);
            
                extr3(window, input);
            
                extr4(window, input);
            
        }

};/**
 * Binary classification chain
 * Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:min(mx)', 'moments:max(mx)', 'moments:mean(mx)', 'moments:min(abs(mx))', 'moments:max(abs(mx))', 'moments:mean(abs(mx))', 'moments:std(mx)', 'moments:min(my)', 'moments:max(my)', 'moments:mean(my)', 'moments:min(abs(my))', 'moments:min(mz)', 'moments:std(mz)', 'autocorrelation(my)', 'peaks(my)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
 */
 // feature extractors

/**
 * Moments()
 */
class _Ohx7Rx__moments_133891445037328_8368215314833 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: mx
                extract(window.data[0] + window.length - 76, &(input._XiOuCe__momentsminmx), &(input._kIX8Zh__momentsmaxmx), &(input._jSiICE__momentsmeanmx), &(input._IknBSj__momentsminabsmx), &(input._ypwfnt__momentsmaxabsmx), &(input._lnNby7__momentsmeanabsmx), &(input._vI9LHD__momentsstdmx) );
            
                // dimension: my
                extract(window.data[1] + window.length - 76, &(input._SalQct__momentsminmy), &(input._HRgdF2__momentsmaxmy), &(input._FkO1dy__momentsmeanmy), &(input._Oic8kL__momentsminabsmy), &(input._SxHu89__momentsmaxabsmy), &(input._x2BxiN__momentsmeanabsmy), &(input._F5bOdo__momentsstdmy) );
            
                // dimension: mz
                extract(window.data[2] + window.length - 76, &(input._082CHh__momentsminmz), &(input._EklLmr__momentsmaxmz), &(input._hqsjUF__momentsmeanmz), &(input._b2Fi2p__momentsminabsmz), &(input._clg7v2__momentsmaxabsmz), &(input._15tt2v__momentsmeanabsmz), &(input._Znwbtu__momentsstdmz) );
            
        }

    protected:

        void extract(float *array, float *minimum, float *maximum, float *average, float *absminimum, float *absmaximum, float *absaverage, float *stddev) {
            const float inverseCount = 0.013157894736842105f;
            float sum = 0;
            float absum = 0;
            float m = 3.402823466e+38F;
            float M = -3.402823466e+38F;
            float absm = 3.402823466e+38F;
            float absM = 0;

            // first pass (min, max, mean)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float a = math::absolute(v);

                sum += v;
                absum += a;

                if (v < m) m = v;
                if (v > M) M = v;
                if (a < absm) absm = a;
                if (a > absM) absM = a;
            }

            const float mean = sum * inverseCount;
            float var = 0;
            float skew = 0;
            float kurtosis = 0;

            *minimum = m;
            *maximum = M;
            *average = mean;
            *absminimum = absm;
            *absmaximum = absM;
            *absaverage = absum * inverseCount;

            // second pass (std, skew, kurtosis)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float d = v - mean;
                const float s = pow(d, 3);

                var += d * d;
                //skew += s;
                //kurtosis += s * d; // a.k.a. d^4
            }

            *stddev = std::sqrt(var * inverseCount);
            //*skew = sk / pow(var, 1.5) * inverseCount;
            //*kurtosis = kurt / pow(var, 2) * inverseCount;
        }
};

/**
 * Autocorrelation(lag=1)
 */
class _rhjPN3__autocorrelation_133891436653264_8368214790829 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._9XogdU__autocorrelationmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._j861DZ__autocorrelationmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._u0yBgY__autocorrelationmz));
            
        }

    protected:

        void extract(float *array, float *autocorrelation) {
            const float mean = np::mean(array, 76);
            float num = 0;
            float den = (array[0] - mean) * (array[0] - mean);

            // second pass (autocorrelation)
            for (uint16_t i = 1; i < 76; i++) {
                const float current = array[i - 1] - mean;
                const float next = array[i] - mean;

                num += current * next;
                den += next * next;
            }

            *autocorrelation = num / den;
        }
};

/**
 * Peaks(magnitude=0.1)
 */
class _8cREW5__peaks_133891448184336_8368215511521 {
    public:

        void operator()(Window& window, Input& input) {
            
        }

    protected:

        void extract(float *array, float *peaksCount) {
            const float thres = (np::maximum(array, 76) - np::minimum(array, 76)) * 0.1f;
            uint16_t peaks = 0;

            for (uint16_t i = 1; i < 76 - 1; i++) {
                const float prev = array[i - 1];
                const float curr = array[i];
                const float next = array[i + 1];

                // check if peak
                if (math::absolute(curr - prev) > thres && math::absolute(curr - next) > thres)
                    peaks++;
            }

            *peaksCount = peaks / 74.0f;
        }
};

/**
 * CountAboveMean()
 */
class _NZoR7Z__countabovemean_133891455411728_8368215963233 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._zZmGqV__count_above_meanmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._fz7hE5__count_above_meanmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._V7ILZq__count_above_meanmz));
            
        }

    protected:

        void extract(float *array, float *countAboveMean) {
            const float mean = np::mean(array, 76);
            uint32_t count = 0;

            // second pass (count)
            for (uint16_t i = 0; i < 76; i++) {
                if (array[i] > mean)
                    count++;
            }

            *countAboveMean = count / 76f;
        }
};


// ovr block

class _QP0UkO__select_133891434906704_8368214681669 {
    public:

        /**
         * Perform feature selection
         */
        void operator()(Input& input, Output& output) {
            // nothing to do, feature selection is only needed in Python
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }
};

/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1121168501)
 */
class _o4v4qb__decisiontree_133891433120080_8368214570005 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._ypwfnt__momentsmaxabsmx < 0.5092698335647583f) {
        
    if (input._Znwbtu__momentsstdmz < 0.12045497074723244f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925;
    return;

    }
    else {
        
    if (input._kIX8Zh__momentsmaxmx < 0.4908369481563568f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925;
    return;

    }

    }

    }
    else {
        
    if (input._ypwfnt__momentsmaxabsmx < 0.7012512385845184f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.075;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.925;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=977856031)
 */
class _F4hyle__decisiontree_133891439965328_8368214997833 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._ZP45RY__peaksmy < 0.11486486718058586f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9541666666666667;
    return;

    }
    else {
        
    if (input._lnNby7__momentsmeanabsmx < 0.41333578526973724f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.04583333333333333;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9541666666666667;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1219083872)
 */
class _cxML0Q__decisiontree_133891433460496_8368214591281 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._HRgdF2__momentsmaxmy < 0.7546454071998596f) {
        
    if (input._082CHh__momentsminmz < 0.24206912517547607f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9083333333333333;
    return;

    }
    else {
        
    if (input._jSiICE__momentsmeanmx < 0.40453876554965973f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9083333333333333;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9083333333333333;
    return;

    }

    }

    }
    else {
        
    if (input._ZP45RY__peaksmy < 0.10135134682059288f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9083333333333333;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.09166666666666666;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1136069129)
 */
class _kiLVGk__decisiontree_133891433738832_8368214608677 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._vI9LHD__momentsstdmx < 0.14793407917022705f) {
        
    if (input._vI9LHD__momentsstdmx < 0.049570148810744286f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9375;
    return;

    }
    else {
        
    if (input._ypwfnt__momentsmaxabsmx < 0.47871367633342743f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9375;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9375;
    return;

    }

    }

    }
    else {
        
    if (input._j861DZ__autocorrelationmy < 0.9064837396144867f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9375;
    return;

    }
    else {
        
    if (input._lnNby7__momentsmeanabsmx < 0.2753146141767502f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.0625;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9375;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1991416347)
 */
class _imJbsk__decisiontree_133891434515664_8368214657229 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._HRgdF2__momentsmaxmy < 0.9442465603351593f) {
        
    if (input._j861DZ__autocorrelationmy < 0.9423038959503174f) {
        
    if (input._ZP45RY__peaksmy < 0.11486486718058586f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9125;
    return;

    }
    else {
        
    if (input._SalQct__momentsminmy < 0.5601063370704651f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.0875;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9125;
    return;

    }

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9125;
    return;

    }

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.0875;
    return;

    }

            
        }

        bool isReady() {
            return true;
        }
};

class _B2bnBM__randomforest_133891433166992_8368214572937 {
    public:
        void operator()(Input& input, Output& output) {
            Output treeOutput;
            float scores[2] = { 0 };

            // iterate over trees
            
                tree1(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree2(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree3(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree4(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree5(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            

            // get output with highest vote
            output.classification.idx = 0;
            output.classification.confidence = scores[0];

            for (uint8_t i = 1; i < 2; i++) {
                if (scores[i] > output.classification.confidence) {
                    output.classification.idx = i;
                    output.classification.confidence = scores[i];
                }
            }
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }

    protected:
        
            _o4v4qb__decisiontree_133891433120080_8368214570005 tree1;
        
            _F4hyle__decisiontree_133891439965328_8368214997833 tree2;
        
            _cxML0Q__decisiontree_133891433460496_8368214591281 tree3;
        
            _kiLVGk__decisiontree_133891433738832_8368214608677 tree4;
        
            _imJbsk__decisiontree_133891434515664_8368214657229 tree5;
        
};


// chain
class _gBpgwo__binarychain_133891433772944_8368214610809 {
    public:

    _gBpgwo__binarychain_133891433772944_8368214610809() : ready(false) {

    }

    void operator()(Window& window, Input& input, Output& output) {
        extractFeatures(window, input);

        // ovr
        
            block1(input, output);

            if (!block1.isReady()) {
                ready = false;
                return;
            }
        
            block2(input, output);

            if (!block2.isReady()) {
                ready = false;
                return;
            }
        

        ready = true;
    }

    bool isReady() {
        return ready;
    }

    protected:
        bool ready;

        
            _Ohx7Rx__moments_133891445037328_8368215314833 extr1;
        
            _rhjPN3__autocorrelation_133891436653264_8368214790829 extr2;
        
            _8cREW5__peaks_133891448184336_8368215511521 extr3;
        
            _NZoR7Z__countabovemean_133891455411728_8368215963233 extr4;
        

        
            // Select(columns=['moments:min(mx)', 'moments:max(mx)', 'moments:mean(mx)', 'moments:min(abs(mx))', 'moments:max(abs(mx))', 'moments:mean(abs(mx))', 'moments:std(mx)', 'moments:min(my)', 'moments:max(my)', 'moments:mean(my)', 'moments:min(abs(my))', 'moments:min(mz)', 'moments:std(mz)', 'autocorrelation(my)', 'peaks(my)'])
            _QP0UkO__select_133891434906704_8368214681669 block1;
        
            // RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)
            _B2bnBM__randomforest_133891433166992_8368214572937 block2;
        

        void extractFeatures(Window& window, Input& input) {
            
                extr1(window, input);
            
                extr2(window, input);
            
                extr3(window, input);
            
                extr4(window, input);
            
        }

};/**
 * Binary classification chain
 * Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:min(mx)', 'moments:mean(mx)', 'moments:min(abs(mx))', 'moments:std(mx)', 'moments:min(my)', 'moments:mean(my)', 'moments:min(abs(my))', 'moments:max(abs(my))', 'moments:std(my)', 'moments:min(mz)', 'moments:max(mz)', 'moments:min(abs(mz))', 'autocorrelation(mz)', 'peaks(mx)', 'count_above_mean(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
 */
 // feature extractors

/**
 * Moments()
 */
class _jysMT9__moments_133891434911248_8368214681953 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: mx
                extract(window.data[0] + window.length - 76, &(input._XiOuCe__momentsminmx), &(input._kIX8Zh__momentsmaxmx), &(input._jSiICE__momentsmeanmx), &(input._IknBSj__momentsminabsmx), &(input._ypwfnt__momentsmaxabsmx), &(input._lnNby7__momentsmeanabsmx), &(input._vI9LHD__momentsstdmx) );
            
                // dimension: my
                extract(window.data[1] + window.length - 76, &(input._SalQct__momentsminmy), &(input._HRgdF2__momentsmaxmy), &(input._FkO1dy__momentsmeanmy), &(input._Oic8kL__momentsminabsmy), &(input._SxHu89__momentsmaxabsmy), &(input._x2BxiN__momentsmeanabsmy), &(input._F5bOdo__momentsstdmy) );
            
                // dimension: mz
                extract(window.data[2] + window.length - 76, &(input._082CHh__momentsminmz), &(input._EklLmr__momentsmaxmz), &(input._hqsjUF__momentsmeanmz), &(input._b2Fi2p__momentsminabsmz), &(input._clg7v2__momentsmaxabsmz), &(input._15tt2v__momentsmeanabsmz), &(input._Znwbtu__momentsstdmz) );
            
        }

    protected:

        void extract(float *array, float *minimum, float *maximum, float *average, float *absminimum, float *absmaximum, float *absaverage, float *stddev) {
            const float inverseCount = 0.013157894736842105f;
            float sum = 0;
            float absum = 0;
            float m = 3.402823466e+38F;
            float M = -3.402823466e+38F;
            float absm = 3.402823466e+38F;
            float absM = 0;

            // first pass (min, max, mean)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float a = math::absolute(v);

                sum += v;
                absum += a;

                if (v < m) m = v;
                if (v > M) M = v;
                if (a < absm) absm = a;
                if (a > absM) absM = a;
            }

            const float mean = sum * inverseCount;
            float var = 0;
            float skew = 0;
            float kurtosis = 0;

            *minimum = m;
            *maximum = M;
            *average = mean;
            *absminimum = absm;
            *absmaximum = absM;
            *absaverage = absum * inverseCount;

            // second pass (std, skew, kurtosis)
            for (uint16_t i = 0; i < 76; i++) {
                const float v = array[i];
                const float d = v - mean;
                const float s = pow(d, 3);

                var += d * d;
                //skew += s;
                //kurtosis += s * d; // a.k.a. d^4
            }

            *stddev = std::sqrt(var * inverseCount);
            //*skew = sk / pow(var, 1.5) * inverseCount;
            //*kurtosis = kurt / pow(var, 2) * inverseCount;
        }
};

/**
 * Autocorrelation(lag=1)
 */
class _EfTAQR__autocorrelation_133891434911312_8368214681957 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._9XogdU__autocorrelationmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._j861DZ__autocorrelationmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._u0yBgY__autocorrelationmz));
            
        }

    protected:

        void extract(float *array, float *autocorrelation) {
            const float mean = np::mean(array, 76);
            float num = 0;
            float den = (array[0] - mean) * (array[0] - mean);

            // second pass (autocorrelation)
            for (uint16_t i = 1; i < 76; i++) {
                const float current = array[i - 1] - mean;
                const float next = array[i] - mean;

                num += current * next;
                den += next * next;
            }

            *autocorrelation = num / den;
        }
};

/**
 * Peaks(magnitude=0.1)
 */
class _wmTMzW__peaks_133891434911376_8368214681961 {
    public:

        void operator()(Window& window, Input& input) {
            
        }

    protected:

        void extract(float *array, float *peaksCount) {
            const float thres = (np::maximum(array, 76) - np::minimum(array, 76)) * 0.1f;
            uint16_t peaks = 0;

            for (uint16_t i = 1; i < 76 - 1; i++) {
                const float prev = array[i - 1];
                const float curr = array[i];
                const float next = array[i + 1];

                // check if peak
                if (math::absolute(curr - prev) > thres && math::absolute(curr - next) > thres)
                    peaks++;
            }

            *peaksCount = peaks / 74.0f;
        }
};

/**
 * CountAboveMean()
 */
class _xPCrE8__countabovemean_133891434911440_8368214681965 {
    public:

        void operator()(Window& window, Input& input) {
            
                // dimension: 
                extract(window.data[0] + window.length - 76, &(input._zZmGqV__count_above_meanmx));
            
                // dimension: 
                extract(window.data[1] + window.length - 76, &(input._fz7hE5__count_above_meanmy));
            
                // dimension: 
                extract(window.data[2] + window.length - 76, &(input._V7ILZq__count_above_meanmz));
            
        }

    protected:

        void extract(float *array, float *countAboveMean) {
            const float mean = np::mean(array, 76);
            uint32_t count = 0;

            // second pass (count)
            for (uint16_t i = 0; i < 76; i++) {
                if (array[i] > mean)
                    count++;
            }

            *countAboveMean = count / 76f;
        }
};


// ovr block

class _FdH99z__select_133891434911184_8368214681949 {
    public:

        /**
         * Perform feature selection
         */
        void operator()(Input& input, Output& output) {
            // nothing to do, feature selection is only needed in Python
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }
};

/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=583570742)
 */
class _xLb7lL__decisiontree_133891436648656_8368214790541 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._SalQct__momentsminmy < 0.10926155094057322f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.09606986899563319;
    return;

    }
    else {
        
    if (input._vI9LHD__momentsstdmx < 0.14594606310129166f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9039301310043668;
    return;

    }
    else {
        
    if (input._FkO1dy__momentsmeanmy < 0.5702885091304779f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.9039301310043668;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.09606986899563319;
    return;

    }

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=1080925887)
 */
class _kA3kpg__decisiontree_133891432876688_8368214554793 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._vI9LHD__momentsstdmx < 0.2284720242023468f) {
        
    if (input._XiOuCe__momentsminmx < 0.007660028524696827f) {
        
    if (input._Oic8kL__momentsminabsmy < 0.41783662140369415f) {
        
    if (input._u0yBgY__autocorrelationmz < 0.9518709480762482f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.11353711790393013;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.11353711790393013;
    return;

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8864628820960698;
    return;

    }

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.11353711790393013;
    return;

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=743997022)
 */
class _k92pOQ__decisiontree_133891432884624_8368214555289 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._SalQct__momentsminmy < 0.10926155094057322f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.1222707423580786;
    return;

    }
    else {
        
    if (input._XiOuCe__momentsminmx < 0.007660028524696827f) {
        
    if (input._F5bOdo__momentsstdmy < 0.05632765591144562f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.1222707423580786;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8777292576419214;
    return;

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8777292576419214;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=552976042)
 */
class _zt5iWT__decisiontree_133891434051536_8368214628221 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._u0yBgY__autocorrelationmz < 0.9207612574100494f) {
        
    if (input._IknBSj__momentsminabsmx < 0.02843518741428852f) {
        
    if (input._SxHu89__momentsmaxabsmy < 0.7529420852661133f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.10043668122270742;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.10043668122270742;
    return;

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8995633187772926;
    return;

    }

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8995633187772926;
    return;

    }

            
        }

        bool isReady() {
            return true;
        }
};/**
 * DecisionTreeClassifier(max_depth=7, max_features='sqrt', min_samples_leaf=5,
                       random_state=413830481)
 */
class _RwE7UJ__decisiontree_133891434848848_8368214678053 {
    public:

        void operator()(Input& input, Output& output) {
            
                
    if (input._082CHh__momentsminmz < 0.02352178283035755f) {
        
    if (input._SalQct__momentsminmy < 0.10926155094057322f) {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.13537117903930132;
    return;

    }
    else {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8646288209606987;
    return;

    }

    }
    else {
        
    if (input._vI9LHD__momentsstdmx < 0.10876987874507904f) {
        
    output.classification.idx = 0;
    output.classification.confidence = 0.8646288209606987;
    return;

    }
    else {
        
    output.classification.idx = 1;
    output.classification.confidence = 0.13537117903930132;
    return;

    }

    }

            
        }

        bool isReady() {
            return true;
        }
};

class _SNJHl2__randomforest_133891434911504_8368214681969 {
    public:
        void operator()(Input& input, Output& output) {
            Output treeOutput;
            float scores[2] = { 0 };

            // iterate over trees
            
                tree1(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree2(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree3(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree4(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            
                tree5(input, treeOutput);
                scores[treeOutput.classification.idx] += 1;
            

            // get output with highest vote
            output.classification.idx = 0;
            output.classification.confidence = scores[0];

            for (uint8_t i = 1; i < 2; i++) {
                if (scores[i] > output.classification.confidence) {
                    output.classification.idx = i;
                    output.classification.confidence = scores[i];
                }
            }
        }

        /**
         * Always ready
         */
        bool isReady() {
            return true;
        }

    protected:
        
            _xLb7lL__decisiontree_133891436648656_8368214790541 tree1;
        
            _kA3kpg__decisiontree_133891432876688_8368214554793 tree2;
        
            _k92pOQ__decisiontree_133891432884624_8368214555289 tree3;
        
            _zt5iWT__decisiontree_133891434051536_8368214628221 tree4;
        
            _RwE7UJ__decisiontree_133891434848848_8368214678053 tree5;
        
};


// chain
class _PxfoH7__binarychain_133891434910800_8368214681925 {
    public:

    _PxfoH7__binarychain_133891434910800_8368214681925() : ready(false) {

    }

    void operator()(Window& window, Input& input, Output& output) {
        extractFeatures(window, input);

        // ovr
        
            block1(input, output);

            if (!block1.isReady()) {
                ready = false;
                return;
            }
        
            block2(input, output);

            if (!block2.isReady()) {
                ready = false;
                return;
            }
        

        ready = true;
    }

    bool isReady() {
        return ready;
    }

    protected:
        bool ready;

        
            _jysMT9__moments_133891434911248_8368214681953 extr1;
        
            _EfTAQR__autocorrelation_133891434911312_8368214681957 extr2;
        
            _wmTMzW__peaks_133891434911376_8368214681961 extr3;
        
            _xPCrE8__countabovemean_133891434911440_8368214681965 extr4;
        

        
            // Select(columns=['moments:min(mx)', 'moments:mean(mx)', 'moments:min(abs(mx))', 'moments:std(mx)', 'moments:min(my)', 'moments:mean(my)', 'moments:min(abs(my))', 'moments:max(abs(my))', 'moments:std(my)', 'moments:min(mz)', 'moments:max(mz)', 'moments:min(abs(mz))', 'autocorrelation(mz)', 'peaks(mx)', 'count_above_mean(mz)'])
            _FdH99z__select_133891434911184_8368214681949 block1;
        
            // RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)
            _SNJHl2__randomforest_133891434911504_8368214681969 block2;
        

        void extractFeatures(Window& window, Input& input) {
            
                extr1(window, input);
            
                extr2(window, input);
            
                extr3(window, input);
            
                extr4(window, input);
            
        }

};

    /**
     * Chain class
     * Chain(blocks=[Scale(method=minmax, offsets=[-400. -400. -400.], scales=[799.987793 709.49707  799.987793]), Window(features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()], chunk=0 days 00:00:00.250000, shift=0 days 00:00:00.250000), Select(config={'include': None, 'exclude': None, 'kbest': None, 'rfe': {'k': None, 'estimator': None}, 'sequential': {'k': 'auto', 'direction': 'forward', 'estimator': None}}), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
     */
     class MediaControlChain {
        public:
            Input input;
            Output output;
            String label;
            Input inputs[3];
            Output outputs[3];
            Classmap classmap;

            /**
 * Transform Input
 */
bool operator()(const Input& input) {
    return operator()(input._PSawsX__mx, input._aGTzid__my, input._Tz3Q7P__mz);
}

/**
 * Transform array input
 */
bool operator()(float *inputs) {
    return operator()(inputs[0], inputs[1], inputs[2]);
}

/**
 * Transform const array input
 */
bool operator()(const float *inputs) {
    return operator()(inputs[0], inputs[1], inputs[2]);
}


            /**
             * Transform input
             */
            bool operator()(const float _PSawsX__mx, const float _aGTzid__my, const float _Tz3Q7P__mz) {
                // assign variables to input
                
                    input._PSawsX__mx = _PSawsX__mx;
                
                    input._aGTzid__my = _aGTzid__my;
                
                    input._Tz3Q7P__mz = _Tz3Q7P__mz;
                

                
                    // run pre-processing blocks
                    if (!pre(input._PSawsX__mx, input._aGTzid__my, input._Tz3Q7P__mz))
                        return false;

                    // copy pre.input to input
                    
                        input._PSawsX__mx = pre.input._PSawsX__mx;
                    
                        input._aGTzid__my = pre.input._aGTzid__my;
                    
                        input._Tz3Q7P__mz = pre.input._Tz3Q7P__mz;
                    
                


                // windowing
                window(input);

                if (!window.isReady())
                    return false;

                // feature extraction + ovr for each binary classification chain
                
                    inputs[0].copyFrom(input);
                    chain1(window, inputs[0], outputs[0]);
                
                    inputs[1].copyFrom(input);
                    chain2(window, inputs[1], outputs[1]);
                
                    inputs[2].copyFrom(input);
                    chain3(window, inputs[2], outputs[2]);
                

                // get positive classification with highest confidence
                int8_t idx = -1;
                float confidence = 0;

                for (uint8_t i = 0; i < 3; i++) {
                    if (outputs[i].classification.idx > 0 && outputs[i].classification.confidence > confidence) {
                        idx = i;
                        confidence = outputs[i].classification.confidence;
                    }
                }

                output.classification.prevIdx = output.classification.idx;
                output.classification.prevConfidence = output.classification.confidence;
                output.classification.idx = idx;
                output.classification.confidence = confidence;
                output.classification.label = classmap.get(idx);
                label = output.classification.label;

                return true;
            }

        protected:
            
            internals::tinyml4all::PreprocessingChain pre;
            
            Window window;
            
                // Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:max(mx)', 'moments:mean(mx)', 'moments:min(abs(mx))', 'moments:max(abs(mx))', 'moments:mean(abs(mx))', 'moments:max(my)', 'moments:mean(my)', 'moments:min(abs(my))', 'moments:max(abs(my))', 'moments:max(mz)', 'moments:mean(mz)', 'moments:min(abs(mz))', 'moments:max(abs(mz))', 'peaks(mx)', 'peaks(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
                _LDQLSZ__binarychain_133891439963664_8368214997729 chain1;
            
                // Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:min(mx)', 'moments:max(mx)', 'moments:mean(mx)', 'moments:min(abs(mx))', 'moments:max(abs(mx))', 'moments:mean(abs(mx))', 'moments:std(mx)', 'moments:min(my)', 'moments:max(my)', 'moments:mean(my)', 'moments:min(abs(my))', 'moments:min(mz)', 'moments:std(mz)', 'autocorrelation(my)', 'peaks(my)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
                _gBpgwo__binarychain_133891433772944_8368214610809 chain2;
            
                // Chain(blocks=[Window(length=1.0s, shift=0.25s, features=[Moments(), Autocorrelation(lag=1), Peaks(magnitude=0.1), CountAboveMean()]), Select(columns=['moments:min(mx)', 'moments:mean(mx)', 'moments:min(abs(mx))', 'moments:std(mx)', 'moments:min(my)', 'moments:mean(my)', 'moments:min(abs(my))', 'moments:max(abs(my))', 'moments:std(my)', 'moments:min(mz)', 'moments:max(mz)', 'moments:min(abs(mz))', 'autocorrelation(mz)', 'peaks(mx)', 'count_above_mean(mz)']), RandomForestClassifier(max_depth=7, min_samples_leaf=5, n_estimators=5)])
                _PxfoH7__binarychain_133891434910800_8368214681925 chain3;
            

            String getLabel(int8_t idx) {
                switch (idx) {
                    
                    default: return "unknown";
                }
            }
     };
}